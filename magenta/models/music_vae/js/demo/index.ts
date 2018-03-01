// tslint:disable-next-line:max-line-length
import { MusicVAE, DrumsConverter, DrumRollConverter, MelodyConverter, INoteSequence} from '../index';
import * as dl from 'deeplearn';

// tslint:disable:max-line-length
const DRUMS_CKPT = 'https://storage.googleapis.com/download.magenta.tensorflow.org/models/music_vae/dljs/drums_small_hikl';
const DRUMS_NADE_CKPT = 'https://storage.googleapis.com/download.magenta.tensorflow.org/models/music_vae/dljs/drums_nade_9';
const MEL_CKPT = 'https://storage.googleapis.com/download.magenta.tensorflow.org/models/music_vae/dljs/mel_small';
// tslint:enable:max-line-length
const DRUM_SEQS: INoteSequence[] = [
  {notes: [
  {pitch: 36, quantizedStartStep: 0},
  {pitch: 42, quantizedStartStep: 2},
  {pitch: 36, quantizedStartStep: 4},
  {pitch: 42, quantizedStartStep: 6},
  {pitch: 36, quantizedStartStep: 8},
  {pitch: 42, quantizedStartStep: 10},
  {pitch: 36, quantizedStartStep: 12},
  {pitch: 42, quantizedStartStep: 14},
  {pitch: 36, quantizedStartStep: 16},
  {pitch: 36, quantizedStartStep: 24},
  {pitch: 36, quantizedStartStep: 28},
  {pitch: 42, quantizedStartStep: 30}
  ]},
  {notes: [
  {pitch: 36, quantizedStartStep: 0}, {pitch: 38, quantizedStartStep: 0},
  {pitch: 42, quantizedStartStep: 0}, {pitch: 46, quantizedStartStep: 0},
  {pitch: 42, quantizedStartStep: 2}, {pitch: 42, quantizedStartStep: 3},
  {pitch: 42, quantizedStartStep: 4}, {pitch: 50, quantizedStartStep: 4},
  {pitch: 36, quantizedStartStep: 6}, {pitch: 38, quantizedStartStep: 6},
  {pitch: 42, quantizedStartStep: 6}, {pitch: 45, quantizedStartStep: 6},
  {pitch: 36, quantizedStartStep: 8}, {pitch: 42, quantizedStartStep: 8},
  {pitch: 46, quantizedStartStep: 8}, {pitch: 42, quantizedStartStep: 10},
  {pitch: 48, quantizedStartStep: 10}, {pitch: 50, quantizedStartStep: 10},
  {pitch: 36, quantizedStartStep: 12}, {pitch: 38, quantizedStartStep: 12},
  {pitch: 42, quantizedStartStep: 12}, {pitch: 48, quantizedStartStep: 12},
  {pitch: 50, quantizedStartStep: 13}, {pitch: 42, quantizedStartStep: 14},
  {pitch: 45, quantizedStartStep: 14}, {pitch: 48, quantizedStartStep: 14},
  {pitch: 36, quantizedStartStep: 16}, {pitch: 38, quantizedStartStep: 16},
  {pitch: 42, quantizedStartStep: 16}, {pitch: 46, quantizedStartStep: 16},
  {pitch: 49, quantizedStartStep: 16}, {pitch: 42, quantizedStartStep: 18},
  {pitch: 42, quantizedStartStep: 19}, {pitch: 42, quantizedStartStep: 20},
  {pitch: 50, quantizedStartStep: 20}, {pitch: 36, quantizedStartStep: 22},
  {pitch: 38, quantizedStartStep: 22}, {pitch: 42, quantizedStartStep: 22},
  {pitch: 45, quantizedStartStep: 22}, {pitch: 36, quantizedStartStep: 24},
  {pitch: 42, quantizedStartStep: 24}, {pitch: 46, quantizedStartStep: 24},
  {pitch: 42, quantizedStartStep: 26}, {pitch: 48, quantizedStartStep: 26},
  {pitch: 50, quantizedStartStep: 26}, {pitch: 36, quantizedStartStep: 28},
  {pitch: 38, quantizedStartStep: 28}, {pitch: 42, quantizedStartStep: 28},
  {pitch: 42, quantizedStartStep: 30}, {pitch: 48, quantizedStartStep: 30}
  ]},
  {notes: [
  {pitch: 38, quantizedStartStep: 0}, {pitch: 42, quantizedStartStep: 0},
  {pitch: 42, quantizedStartStep: 2}, {pitch: 42, quantizedStartStep: 4},
  {pitch: 36, quantizedStartStep: 6}, {pitch: 38, quantizedStartStep: 6},
  {pitch: 42, quantizedStartStep: 6}, {pitch: 45, quantizedStartStep: 6},
  {pitch: 36, quantizedStartStep: 8}, {pitch: 42, quantizedStartStep: 8},
  {pitch: 42, quantizedStartStep: 10}, {pitch: 38, quantizedStartStep: 12},
  {pitch: 42, quantizedStartStep: 12}, {pitch: 45, quantizedStartStep: 12},
  {pitch: 36, quantizedStartStep: 14}, {pitch: 42, quantizedStartStep: 14},
  {pitch: 46, quantizedStartStep: 14}, {pitch: 36, quantizedStartStep: 16},
  {pitch: 42, quantizedStartStep: 16}, {pitch: 42, quantizedStartStep: 18},
  {pitch: 38, quantizedStartStep: 20}, {pitch: 42, quantizedStartStep: 20},
  {pitch: 45, quantizedStartStep: 20}, {pitch: 36, quantizedStartStep: 22},
  {pitch: 42, quantizedStartStep: 22}, {pitch: 36, quantizedStartStep: 24},
  {pitch: 42, quantizedStartStep: 24}, {pitch: 38, quantizedStartStep: 26},
  {pitch: 42, quantizedStartStep: 26}, {pitch: 45, quantizedStartStep: 26},
  {pitch: 42, quantizedStartStep: 28}, {pitch: 45, quantizedStartStep: 28},
  {pitch: 36, quantizedStartStep: 30}, {pitch: 42, quantizedStartStep: 30},
  {pitch: 45, quantizedStartStep: 30}
  ]},
  {notes: [
  {pitch: 50, quantizedStartStep: 4}, {pitch: 50, quantizedStartStep: 20}
  ]}];

function writeTimer(elementId: string, startTime: number) {
  document.getElementById(elementId).innerHTML = (
  (performance.now() - startTime) / 1000.).toString() + 's';
}

function writeNoteSeqs(elementId: string, seqs: INoteSequence[]) {
  document.getElementById(elementId).innerHTML = seqs.map(
  seq => '[' + seq.notes.map(n => {
    let s = '{p:' + n.pitch + ' s:' + n.quantizedStartStep;
    if (n.quantizedEndStep != null) {
      s += ' e:' +  n.quantizedEndStep;
    }
    s += '}';
    return s;
  }).join(', ') + ']').join('<br>');
}

async function runDrums(){
  const mvae: MusicVAE = new MusicVAE(DRUMS_CKPT, new DrumsConverter(32));
  await mvae.initialize();

  writeNoteSeqs('drums-inputs', DRUM_SEQS);

  let start = performance.now();

  const interp = mvae.interpolate(DRUM_SEQS, 3);
  writeTimer('drums-interp-time', start);
  writeNoteSeqs('drums-interp', interp);

  start = performance.now();
  const sample = mvae.sample(5);
  writeTimer('drums-sample-time', start);
  writeNoteSeqs('drums-samples', sample);

  mvae.dispose();
  console.log(dl.memory());
}

async function runDrumsNade(){
  const mvae: MusicVAE = new MusicVAE(
  DRUMS_NADE_CKPT, new DrumRollConverter(32));
  await mvae.initialize();

  writeNoteSeqs('nade-inputs', DRUM_SEQS);

  let start = performance.now();
  const interp = mvae.interpolate(DRUM_SEQS, 3);
  writeTimer('nade-interp-time', start);
  writeNoteSeqs('nade-interp', interp);

  start = performance.now();
  const sample = mvae.sample(5);
  writeTimer('nade-sample-time', start);
  writeNoteSeqs('nade-samples', sample);

  mvae.dispose();
  console.log(dl.memory());
}

async function runMel(){
  const mvae:MusicVAE = new MusicVAE(MEL_CKPT, new MelodyConverter(32));
  await mvae.initialize();

  const teaPot: INoteSequence = {notes: [{
  pitch: 69, quantizedStartStep: 0, quantizedEndStep: 2},
  {pitch: 71, quantizedStartStep: 2, quantizedEndStep: 4},
  {pitch: 73, quantizedStartStep: 4, quantizedEndStep: 6},
  {pitch: 74, quantizedStartStep: 6, quantizedEndStep: 8},
  {pitch: 76, quantizedStartStep: 8, quantizedEndStep: 10},
  {pitch: 81, quantizedStartStep: 12, quantizedEndStep: 16},
  {pitch: 77, quantizedStartStep: 16, quantizedEndStep: 20},
  {pitch: 80, quantizedStartStep: 20, quantizedEndStep: 24},
  {pitch: 75, quantizedStartStep: 24, quantizedEndStep: 32}
  ]};

  const twinkle: INoteSequence = {notes: [
  {pitch: 60, quantizedStartStep: 0, quantizedEndStep: 2},
  {pitch: 60, quantizedStartStep: 2, quantizedEndStep: 4},
  {pitch: 67, quantizedStartStep: 4, quantizedEndStep: 6},
  {pitch: 67, quantizedStartStep: 6, quantizedEndStep: 8},
  {pitch: 69, quantizedStartStep: 8, quantizedEndStep: 10},
  {pitch: 69, quantizedStartStep: 10, quantizedEndStep: 12},
  {pitch: 67, quantizedStartStep: 12, quantizedEndStep: 16},
  {pitch: 65, quantizedStartStep: 16, quantizedEndStep: 18},
  {pitch: 65, quantizedStartStep: 18, quantizedEndStep: 20},
  {pitch: 64, quantizedStartStep: 20, quantizedEndStep: 22},
  {pitch: 64, quantizedStartStep: 22, quantizedEndStep: 24},
  {pitch: 62, quantizedStartStep: 24, quantizedEndStep: 26},
  {pitch: 62, quantizedStartStep: 26, quantizedEndStep: 28},
  {pitch: 60, quantizedStartStep: 28, quantizedEndStep: 32}
  ]};

  writeNoteSeqs('mel-inputs', [teaPot, twinkle]);

  let start = performance.now();
  const interp = mvae.interpolate([teaPot, twinkle], 5);
  writeTimer('mel-interp-time', start);
  writeNoteSeqs('mel-interp', interp);

  start = performance.now();
  const sample = mvae.sample(5);
  writeTimer('mel-sample-time', start);
  writeNoteSeqs('mel-samples', sample);

  mvae.dispose();
  console.log(dl.memory());
}

try {
  runDrums();
  runDrumsNade();
  runMel();
} catch (err){
  console.error(err);
}
