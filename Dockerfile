FROM django:latest

ENV PYTHONUNBUFFERED 1

RUN mkdir /requirements
ADD ./requirements/* /requirements/

WORKDIR /requirements
RUN pip install -r dev.txt
