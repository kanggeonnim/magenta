# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""MusicVAE LSTM model utilities."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

# internal imports
import tensorflow as tf

from tensorflow.contrib import rnn
from tensorflow.contrib import seq2seq
from tensorflow.contrib.cudnn_rnn.python.layers import cudnn_rnn
from tensorflow.python.util import nest


def rnn_cell(rnn_cell_size, dropout_keep_prob, is_training=True):
  """Builds an LSTMBlockCell based on the given parameters."""
  dropout_keep_prob = dropout_keep_prob if is_training else 1.0
  cells = []
  for layer_size in rnn_cell_size:
    cell = rnn.LSTMBlockCell(layer_size)
    cell = rnn.DropoutWrapper(
        cell,
        input_keep_prob=dropout_keep_prob)
    cells.append(cell)
  return rnn.MultiRNNCell(cells)


def cudnn_lstm_layer(layer_sizes, dropout_keep_prob, is_training=True,
                     name_or_scope='rnn'):
  """Builds a CudnnLSTM Layer based on the given parameters."""
  dropout_keep_prob = dropout_keep_prob if is_training else 1.0
  for ls in layer_sizes:
    if ls != layer_sizes[0]:
      raise ValueError(
          'CudnnLSTM does not support layers with differing sizes. Got: %s',
          layer_sizes)
  lstm = cudnn_rnn.CudnnLSTM(
      num_layers=len(layer_sizes),
      num_units=layer_sizes[0],
      direction='unidirectional',
      dropout=1.0 - dropout_keep_prob,
      name=name_or_scope)

  class BackwardCompatibleCudnnLSTMSaveable(
      tf.contrib.cudnn_rnn.CudnnLSTMSaveable):
    """Overrides CudnnLSTMSaveable for backward-compatibility."""

    def _cudnn_to_tf_biases(self, *cu_biases):
      """Overrides to subtract 1.0 from `forget_bias` (see BasicLSTMCell)."""
      (tf_bias,) = (
          super(BackwardCompatibleCudnnLSTMSaveable, self)._cudnn_to_tf_biases(
              *cu_biases))
      i, c, f, o = tf.split(tf_bias, 4)
      # Non-Cudnn LSTM cells add 1.0 to the forget bias variable.
      return (tf.concat([i, c, f - 1.0, o], axis=0),)

    def _tf_to_cudnn_biases(self, *tf_biases):
      """Overrides to add 1.0 to `forget_bias` (see BasicLSTMCell)."""
      (tf_bias,) = tf_biases
      i, c, f, o = tf.split(tf_bias, 4)
      # Non-Cudnn LSTM cells add 1.0 to the forget bias variable.
      return (
          super(BackwardCompatibleCudnnLSTMSaveable, self)._tf_to_cudnn_biases(
              tf.concat([i, c, f + 1.0, o], axis=0)))

    def _TFCanonicalNamePrefix(self, layer, is_fwd=True):
      """Overrides for backward-compatible variable names."""
      if self._direction == 'unidirectional':
        return 'multi_rnn_cell/cell_%d/lstm_cell' % layer
      else:
        return (
            'cell_%d/bidirectional_rnn/%s/multi_rnn_cell/cell_0/lstm_cell'
            % (layer, 'fw' if is_fwd else 'bw'))

  lstm._saveable_cls = BackwardCompatibleCudnnLSTMSaveable  # pylint:disable=protected-access
  return lstm


def cudnn_lstm_state(lstm_cell_state):
  """Convert tuple of LSTMCellStateTuples to CudnnLSTM format."""
  h = tf.stack([s.h for s in lstm_cell_state])
  c = tf.stack([s.c for s in lstm_cell_state])
  return (h, c)


def get_final(time_major_sequence, sequence_length):
  """Get the final item in a time-major sequence."""
  final_index = tf.stack(
      [tf.maximum(0, sequence_length - 1),
       tf.range(sequence_length.shape[0])],
      axis=1)
  return tf.gather_nd(time_major_sequence, final_index)


def initial_cell_state_from_embedding(cell, z, name=None):
  """Computes an initial RNN `cell` state from an embedding, `z`."""
  flat_state_sizes = nest.flatten(cell.state_size)
  return nest.pack_sequence_as(
      cell.zero_state(batch_size=z.shape[0], dtype=tf.float32),
      tf.split(
          tf.layers.dense(
              z,
              sum(flat_state_sizes),
              activation=tf.tanh,
              kernel_initializer=tf.random_normal_initializer(stddev=0.001),
              name=name),
          flat_state_sizes,
          axis=1))


def get_sampling_probability(hparams, is_training):
  """Returns the sampling probability as a tensor based on the hparams.

  Supports three sampling schedules (`hparams.sampling_schedule`):
    constant: `hparams.sampling_rate` is the sampling probability. Must be in
      the interval [0, 1].
    exponential: `hparams.sampling_rate` is the base of the decay exponential.
      Must be in the interval (0, 1). Larger values imply a slower increase in
      sampling.
    inverse_sigmoid: `hparams.sampling_rate` is in the interval [1, inf).
      Larger values imply a slower increase in sampling.

  A constant value of 0 is returned if `hparams.sampling_schedule` is undefined.

  If not training and a non-0 sampling schedule is defined, a constant value of
  1 is returned since this is assumed to be a test/eval job associated with a
  scheduled sampling trainer.

  Args:
    hparams: An HParams object containing model hyperparameters.
    is_training: Whether or not the model is being used for training.

  Raises:
    ValueError: On an invalid `sampling_schedule` or `sampling_rate` hparam.
  """
  if (not hasattr(hparams, 'sampling_schedule') or
      not hparams.sampling_schedule or
      (hparams.sampling_schedule == 'constant' and hparams.sampling_rate == 0)):
    return tf.constant(0.0)

  if not is_training:
    # This is likely an eval/test job associated with a training job using
    # scheduled sampling.
    tf.logging.warning(
        'Setting non-training sampling schedule from %s:%f to constant:1.0.',
        hparams.sampling_schedule, hparams.sampling_rate)
    hparams.sampling_schedule = 'constant'
    hparams.sampling_rate = 1.0

  schedule = hparams.sampling_schedule
  rate = hparams.sampling_rate
  step = tf.to_float(tf.train.get_global_step())

  if schedule == 'constant':
    if not 0 <= rate <= 1:
      raise ValueError(
          '`constant` sampling rate must be in the interval [0, 1]. Got %f.'
          % rate)
    sampling_probability = tf.constant(rate)
  elif schedule == 'inverse_sigmoid':
    if rate < 1:
      raise ValueError(
          '`inverse_sigmoid` sampling rate must be at least 1. Got %f.' % rate)
    k = tf.constant(rate)
    sampling_probability = 1.0 - k / (k + tf.exp(step / k))
  elif schedule == 'exponential':
    if not 0 < rate < 1:
      raise ValueError(
          '`exponential` sampling rate must be in the interval (0, 1). Got %f.'
          % hparams.sampling_rate)
    k = tf.constant(rate)
    sampling_probability = 1.0 - tf.pow(k, step)
  else:
    raise ValueError('Invalid `sampling_schedule`: %s' % schedule)
  tf.summary.scalar('sampling_probability', sampling_probability)
  return sampling_probability


class LstmDecodeResults(
    collections.namedtuple('LstmDecodeResults',
                           ('rnn_input', 'rnn_output', 'samples', 'final_state',
                            'final_sequence_lengths'))):
  pass


class Seq2SeqLstmDecoderOutput(
    collections.namedtuple('BasicDecoderOutput',
                           ('rnn_input', 'rnn_output', 'sample_id'))):
  pass


class Seq2SeqLstmDecoder(seq2seq.BasicDecoder):
  """Overrides BaseDecoder to include rnn inputs in the output."""

  def __init__(self, cell, helper, initial_state, output_layer=None):
    if isinstance(helper, seq2seq.TrainingHelper):
      self._input_shape = helper.inputs.shape[2:]
    elif isinstance(helper, seq2seq.InferenceHelper):
      self._input_shape = helper._start_inputs.shape[1:]  # pylint:disable=protected-access
    else:
      raise ValueError('Incompatible `helper` type: %s' % helper.__class__.name)

    super(Seq2SeqLstmDecoder, self).__init__(
        cell, helper, initial_state, output_layer)

  @property
  def output_size(self):
    return Seq2SeqLstmDecoderOutput(
        rnn_input=self._input_shape,
        rnn_output=self._rnn_output_size(),
        sample_id=self._helper.sample_ids_shape)

  @property
  def output_dtype(self):
    dtype = nest.flatten(self._initial_state)[0].dtype
    return Seq2SeqLstmDecoderOutput(
        dtype,
        nest.map_structure(lambda _: dtype, self._rnn_output_size()),
        self._helper.sample_ids_dtype)

  def step(self, time, inputs, state, name=None):
    results = super(Seq2SeqLstmDecoder, self).step(time, inputs, state, name)
    outputs = Seq2SeqLstmDecoderOutput(
        rnn_input=inputs,
        rnn_output=results[0].rnn_output,
        sample_id=results[0].sample_id)
    return (outputs,) + results[1:]

