env :=

DEV_ENV := dev
STAGE_ENV := stage
PROD_ENV := prod

NGINX_HOST = localhost
NGINX_PORT = 8080

GIT_TAG := $(shell git describe --abbrev=0)
VERSION :=

PRIVATE_ENV = ./envs/private.env

ifeq ($(env),$(PROD_ENV))
	DOCKERCOMPOSE_PATH := prod.yml
else ifeq ($(env),$(STAGE_ENV))
	DOCKERCOMPOSE_PATH := prod.yml
else ifeq ($(env),$(DEV_ENV))
	DOCKERCOMPOSE_PATH := dev.yml
else
	DOCKERCOMPOSE_PATH := docker-compose.yml
endif


.PHONY: sh dev.up start debug build .build .migrate \
	.mongo_populate .sql_init .static .mongo_init .stop .rm test version


sh: ${PRIVATE_ENV}
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm dashboard bash

dev.up: ${PRIVATE_ENV}
	docker-compose -f $(DOCKERCOMPOSE_PATH) up -d

start: ${PRIVATE_ENV}
	docker-compose -f $(DOCKERCOMPOSE_PATH) start

debug: ${PRIVATE_ENV}
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm --service-ports dashboard

build: .build .migrate ${PRIVATE_ENV}
ifneq ($(filter $(env),$(STAGE_ENV) $(PROD_ENV)),)
	make .static
endif

.build:
	docker-compose -f $(DOCKERCOMPOSE_PATH) build

.migrate:
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm dashboard \
			python manage.py migrate

.mongo_populate:
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm dashboard \
			python manage.py mongo_setup

.sql_init:
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm dashboard \
			python manage.py loaddata dump.json

.static:
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm dashboard \
			python manage.py collectstatic --noinput

.mongo_init:
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm mongo mongorestore --host=mongo dump

stop:
	docker-compose -f $(DOCKERCOMPOSE_PATH) stop

rm:
	docker-compose -f $(DOCKERCOMPOSE_PATH) rm

test:
	docker-compose -f $(DOCKERCOMPOSE_PATH) run --rm dashboard \
			bash -c \
			" \
			find . | grep -E \"(__pycache__|\.pyc|\.pyo$\)\" | xargs rm -rf && \
			export DJANGO_SETTINGS_MODULE=gamma.settings.test && \
			pytest -s && \
			coverage xml && \
			diff-cover coverage.xml --fail-under=60 \
			"

version:
	echo "Tagged release $(VERSION)\n" > Changelog-$(VERSION).txt
	git log --oneline --no-decorate --no-merges $(GIT_TAG)..HEAD >> Changelog-$(VERSION).txt
	git tag -s -F Changelog-$(VERSION).txt $(VERSION)

${PRIVATE_ENV}:
	touch $@
