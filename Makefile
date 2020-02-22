env :=

DEV_ENV := dev
STAGE_ENV := stage
PROD_ENV := prod

NGINX_HOST = localhost
NGINX_PORT = 8080

GIT_TAG := $(shell git describe --abbrev=0)
VERSION :=

ENV_DIR = ./envs/
LOCAL_ENV = local.env
PRIVATE_ENV = private.env


.PHONY: sh dev.up start debug build .build .migrate \
	.mongo_populate .sql_init .static .mongo_init .stop .rm test version


sh: ${PRIVATE_ENV}
	docker-compose run --rm dashboard bash

dev.up: ${PRIVATE_ENV}
ifneq ($(filter $(env),$(STAGE_ENV) $(PROD_ENV)),)
	docker-compose -f prod.yml up
else ifneq ($(filter $(env),$(DEV_ENV)),)
	docker-compose up
endif

start: ${PRIVATE_ENV}
	docker-compose start

debug: ${PRIVATE_ENV}
	docker-compose run --rm --service-ports dashboard

build: .build .migrate ${PRIVATE_ENV}
ifneq ($(filter $(env),$(STAGE_ENV) $(PROD_ENV)),)
	make .static
endif

.build:
	docker-compose build

.migrate:
	docker-compose run --rm dashboard \
			python manage.py migrate

.mongo_populate:
	docker-compose run --rm dashboard \
			python manage.py mongo_setup

.sql_init:
	docker-compose run --rm dashboard \
			python manage.py loaddata dump.json

.static:
	docker-compose run --rm dashboard \
			python manage.py collectstatic --noinput

.mongo_init:
	docker-compose run --rm mongo mongorestore --host=mongo dump

stop:
	docker-compose stop

rm:
	docker-compose rm

test:
	docker-compose run --rm dashboard \
			bash -c \
			" \
			find . | grep -E \"(__pycache__|\.pyc|\.pyo$\)\" | xargs rm -rf && \
			pytest -s && \
			coverage xml && \
			diff-cover coverage.xml --fail-under=60 \
			"

version:
	echo "Tagged release $(VERSION)\n" > Changelog-$(VERSION).txt
	git log --oneline --no-decorate --no-merges $(GIT_TAG)..HEAD >> Changelog-$(VERSION).txt
	git tag -s -F Changelog-$(VERSION).txt $(VERSION)

${PRIVATE_ENV}:
	touch ${ENV_DIR}$@
