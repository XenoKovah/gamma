FROM python:3.6-slim
LABEL maintainer="cmltaWt0@gmail.com"

RUN apt-get -y update && \
    apt-get install -y \
    git gcc python-dev zlib1g-dev libjpeg-dev mongo-tools

RUN mkdir /requirements
ADD ./requirements/* /requirements/

WORKDIR /requirements
RUN pip install -r test.txt


ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
