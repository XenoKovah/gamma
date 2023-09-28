
FROM node:14 as static
LABEL maintainer="cmltaWt0@gmail.com"

ARG node_env=prod

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN npm ci
RUN npm run build:$node_env


FROM python:3.8-slim as base

RUN apt-get -y update && \
    apt-get install -y \
    git gcc zlib1g-dev libjpeg-dev

RUN mkdir /requirements
COPY ./requirements/* /requirements/

WORKDIR /requirements
RUN pip install --upgrade pip
RUN pip install -r base.txt

RUN apt-get purge -y --auto-remove gcc zlib1g-dev libjpeg-dev

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
COPY . /app

WORKDIR /app

FROM base as production

ARG node_env=prod

COPY --from=static /app/frontend/webpack_bundles frontend/webpack_bundles
COPY --from=static /app/webpack-stats-$node_env.json webpack-stats-$node_env.json


FROM base as development

ARG node_env=dev

WORKDIR /requirements
RUN pip install --upgrade pip
RUN pip install -r test.txt

WORKDIR /app
COPY --from=static /app/frontend/webpack_bundles frontend/webpack_bundles
COPY --from=static /app/webpack-stats-$node_env.json webpack-stats-$node_env.json
