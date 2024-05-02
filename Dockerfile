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
RUN pip install magenta

#
COPY ./ /code/

#
CMD ["python", "server.py"]