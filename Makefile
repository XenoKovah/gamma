env :=

DEV_ENV := dev
STAGE_ENV := stage
PROD_ENV := prod

NGINX_HOST = localhost
NGINX_PORT = 8080

GIT_TAG := $(shell git describe --abbrev=0)
VERSION :=

sh:
	docker-compose run app bash

run:
	docker-compose up

start:
	docker-compose start

debug:
	docker-compose run --service-ports app

build: .build .migrate
ifneq ($(filter $(env),$(STAGE_ENV) $(PROD_ENV)),)
	make .static
endif

.build:
	docker-compose build

.migrate:
	docker-compose run app \
			python manage.py migrate

.mongo_populate:
	docker-compose run app \
			python manage.py mongo_setup

.sql_init:
	docker-compose run app \
			python manage.py loaddata dump.json

.mongo_init:
	docker-compose run mongo mongorestore --host=mongo dump

stop:
	docker-compose  stop

rm:
	docker-compose  rm

test:
	docker-compose  run  app \
			bash -c \
			" \
			find . | grep -E \"(__pycache__|\.pyc|\.pyo$\)\" | xargs rm -rf && \
			pytest && \
			coverage xml && \
			diff-cover coverage.xml --fail-under=60 \
			"

version:
	echo "Tagged release $(VERSION)\n" > Changelog-$(VERSION).txt
	git log --oneline --no-decorate --no-merges $(GIT_TAG)..HEAD >> Changelog-$(VERSION).txt
	git tag -s -F Changelog-$(VERSION).txt $(VERSION)
