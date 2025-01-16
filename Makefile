env :=
# Local devstack can have a lot of trash data
# So we boosting pytest colelction speed
# TODO:
# The gamma already had failed tests due to importing and refactoring.
# So I commented out the other apps and left only the event.
# In the future, all others should be commented out as well.
path := events/api/v0/tests  # core/tests core/notif/tests edx_integration/tests achievements/tests

DEV_ENV := dev
STAGE_ENV := stage
PROD_ENV := prod

GIT_TAG := $(shell git describe --abbrev=0)
VERSION :=

PRIVATE_ENV = ./envs/private.env

CURRENT_DIR = $(shell pwd)
REACT_APP_PATH = "${CURRENT_DIR}/frontend/admin-panel/src"

# Determine the Docker Compose command
DOCKER_COMPOSE := $(shell command -v docker-compose || echo docker compose)

ifeq ($(env),$(PROD_ENV))
	DOCKERCOMPOSE_PATH := prod.yml
else ifeq ($(env),$(STAGE_ENV))
	DOCKERCOMPOSE_PATH := prod.yml
else ifeq ($(env),$(DEV_ENV))
	DOCKERCOMPOSE_PATH := dev.yml
else
	DOCKERCOMPOSE_PATH := docker-compose.yml
endif


.PHONY: shell dev.up start debug build .build .migrate \
		.static .stop .rm test version loadtests test-shell


shell: ${PRIVATE_ENV}
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) run --rm dashboard bash

dev.up: ${PRIVATE_ENV} .static
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) up -d

start: ${PRIVATE_ENV}
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) start

debug: ${PRIVATE_ENV}
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) run --rm --service-ports dashboard \
		bash -c \
		" \
		PYTHONBREAKPOINT=ipdb.set_trace python manage.py runserver 0.0.0.0:9000 \
		"

build: .build .migrate ${PRIVATE_ENV}
ifneq ($(filter $(env),$(STAGE_ENV) $(PROD_ENV)),)
	make .static
endif

.build:
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) build

.migrate:
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) run --rm dashboard \
			python manage.py migrate

.static:
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) run --rm dashboard \
			python manage.py collectstatic --noinput

stop:
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) stop

rm:
	@$(DOCKER_COMPOSE) -f $(DOCKERCOMPOSE_PATH) rm

jest:	# run react tests
	npm run test ${REACT_APP_PATH}

test:
	@$(DOCKER_COMPOSE) -f docker-compose-test.yml run --rm dashboard \
			bash -c \
			" \
			find . | grep -E \"(__pycache__|\.pyc|\.pyo$\)\" | xargs rm -rf && \
			DJANGO_SETTINGS_MODULE=gamma.settings.test \
			PYTHONBREAKPOINT=ipdb.set_trace \
			MONGO_DATABASE=gamma_data_test \
			pytest -W ignore -s -vv --pdb $(path) && \
			coverage xml && \
			diff-cover coverage.xml --fail-under=60 \
			"

test-shell:
	@$(DOCKER_COMPOSE) -f docker-compose-test.yml run --rm dashboard bash

loadtests:
	locust --host=http://localhost:9000 -f loadtests/locustfile.py

quality-py:
	pycodestyle . --format=pylint
	pylint -f colorized -r y gamma/* api/* achievements/* core/* edx_integration/* loadtests/*
	pydocstyle -v gamma/* api/* achievements/* core/* edx_integration/* loadtests/*

version:
	echo "Tagged release $(VERSION)\n" > Changelog-$(VERSION).txt
	git log --oneline --no-decorate --no-merges $(GIT_TAG)..HEAD >> Changelog-$(VERSION).txt
	git tag -s -F Changelog-$(VERSION).txt $(VERSION)

${PRIVATE_ENV}:
	touch $@
