FROM python:3.8-slim
LABEL maintainer="cmltaWt0@gmail.com"

RUN apt-get -y update && \
    apt-get install -y \
    git gcc zlib1g-dev libjpeg-dev

RUN mkdir /requirements
ADD ./requirements/* /requirements/

WORKDIR /requirements
RUN pip install --upgrade pip
RUN pip install -r test.txt

RUN apt-get purge -y --auto-remove gcc zlib1g-dev libjpeg-dev

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
ADD . /app

WORKDIR /app
