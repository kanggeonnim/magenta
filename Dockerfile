FROM ubuntu:latest
LABEL authors="SSAFY"

ENTRYPOINT ["top", "-b"]

#
FROM python:3.7

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --upgrade -r /code/requirements.txt

#
RUN apt-get update && apt-get install -y fluidsynth

#
RUN apt-get update && apt-get install -y ffmpeg

#
COPY ./ /code/

#
CMD ["python", "server.py"]