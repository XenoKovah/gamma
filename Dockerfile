FROM node:18 as static
LABEL maintainer="cmltaWt0@gmail.com"

ARG node_env=prod

RUN mkdir /app
COPY . /app
WORKDIR /app/frontend/gamma

RUN npm ci
RUN npm run build:$node_env

WORKDIR /app

FROM python:3.8-slim as base

RUN apt-get -y update && \
    apt-get install -y \
    git gcc zlib1g-dev libjpeg-dev

RUN mkdir /requirements
COPY ./requirements/* /requirements/

WORKDIR /requirements
RUN pip install --upgrade pip==24.0
RUN pip install -r base.txt

RUN apt-get purge -y --auto-remove gcc zlib1g-dev libjpeg-dev

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
COPY . /app

WORKDIR /app

FROM base as production

ARG node_env=prod

COPY --from=static /app/frontend/gamma/dist /app/frontend/gamma/dist
COPY --from=static /app/frontend/gamma/webpack-stats-$node_env.json /app/frontend/gamma/webpack-stats-$node_env.json

FROM base as development

ARG node_env=dev

WORKDIR /requirements
RUN pip install --upgrade pip==24.0
RUN pip install -r test.txt

WORKDIR /app
COPY --from=static /app/frontend/gamma/dist /app/frontend/gamma/dist
COPY --from=static /app/frontend/gamma/webpack-stats-$node_env.json /app/frontend/gamma/webpack-stats-$node_env.json
