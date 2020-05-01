GAMMA - Gamefication for OpenEdx.
===

GAMMA is a microservice for gamefication.
We provide REST API to work with users coins,
manage Badges or Achievements.


Usage
===
For local development
---
```
✗ npm install
✗ npm run build:dev
✗ make build
✗ make debug
```
Optionally we can use
```
✗ make dev.up env=dev
```


For staging/production usage
---
```
✗ make build
✗ make dev.up env=prod
```


Configuration
===
For docker-compose deployment `env/private.env` file can changed to pass sensitive data into container.
Following sections can be edited to add any sensitive data:

```
# Celery
CELERY_BROKER_URL=amqp://guest@rabbit
CELERY_RESULT_BACKEND=redis://redis:6379

# DB
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Django
# For devstack use DJANGO_SETTINGS_MODULE=gamma.settings.devstack
DJANGO_SETTINGS_MODULE=gamma.settings.production

# React
# Optional reackt backend base url
# For local deployment we can use REACT_APP_LOCALHOST=http://0.0.0.0:9000
REACT_APP_LOCALHOST=

# EDX integrarion
EDX_LMS_BASE_URL=<edx_lms_base_url>
EDX_API_KEY=<edx_api_key>
```


Run loadtests
---

1. export all needed env variables:
```
export APP_KEY=****************
export APP_SECRET==****************
export EVENT_TYPE=edx_bookmark_added
```

2. Create virtualenv
```
mkvirtualenv gamma --python=python3.8
pip install -r requirements/test.txt
```

Currently only one event type is supported.

3. Run locust
```
locust --host=http://localhost:9000 -f loadtests/locustfile.py
```

or use Makefile

```
make loadtests
```

4. Open url http://localhost:8089

5. Start tests
