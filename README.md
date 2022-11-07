GAMMA - Gamification for OpenEdx.
===

GAMMA is a microservice for gamification.
We provide REST API to work with users coins,
manage Badges or Achievements.


Usage
===
For local development
---

Set up `.env` variables. Copy content of the `private.local.example.env` into `private.env` (`<devstack root>/gamma/envs/private.env`). Note that `LOCAL_IP_ADDRESS` can be found using shell command `ifconfig en0` right after `inet` keyword.

Install Gamma application. Note that the Node.js supported version is 12.

```
# Build cloned Gamma repo:
✗ npm install
✗ npm run build:dev
✗ make build

# To run gamma use:
✗ make debug

# You'll need to create a superuser to access the gamma admin site:
✗ make shell
✗ python manage.py createsuperuser
```
Optionally we can use
```
✗ make dev.up env=dev
```

Install [edx-gamma-bridge](https://gitlab.raccoongang.com/products/rg-gamification/gamification-bridge)
and [edx-gamma-dashboard](https://gitlab.raccoongang.com/products/rg-gamification/edx-gamma-dashboard) to the **edx-platform**.

```
# Go to the <devstack root>/src (sibling to the devstack repository)
cd src
git clone https://gitlab.raccoongang.com/products/rg-gamification/gamification-bridge.git
git clone https://gitlab.raccoongang.com/products/rg-gamification/edx-gamma-dashboard.git
cd ../devstack
make lms-shell
pip install -e /edx/src/edx-gamme-bridge
pip install -e /edx/src/edx-gamma-dashboard
exit # exit lms-shell. CTRL + D works as well
make studio-shell
pip install -e /edx/src/edx-gamme-bridge
pip install -e /edx/src/edx-gamma-dashboard
exit # exit lms-shell. CTRL + D works as well
make lms-restart
make studio-restart
```

Gamification settings should be added to the `edx-platform`.

1. Log into the http://0.0.0.0:9000/admin/#/
2. Add new `App client` http://0.0.0.0:9000/admin/core/appclient/add/#/
3. Further settings will use `key` and `secret` from the created `App client`
#### Next step works for Nutmeg only. Use `lms.yml` and `cms.yml` files from `/edx/etc/` inside the container for older edx releases.
4. Go to the `edx-platform/lms/envs/devstack-experimental.yml`
5. Add the following settings.
Note that `LOCAL_IP_ADDRESS` can be found using shell command `ifconfig en0` right after `inet` keyword.

```yml
FEATURES:
    ...
    RG_GAMIFICATION:
        ENABLED: true
        RG_GAMIFICATION_ENDPOINT: http://<LOCAL_IP_ADDRESS>:9000/
        KEY: key
        SECRET: secret
        IGNORED_EVENT_TYPES: []
```
6. The same for the `edx-platform/cms/envs/devstack-experimental.yml`
7. Restart `lms` and `studio` (`make lms-restart && make studio-restart`)

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
# Optional react backend base url
# For local deployment we can use REACT_APP_LOCALHOST=http://0.0.0.0:9000
REACT_APP_LOCALHOST=

# EDX integrarion
EDX_LMS_BASE_URL=<edx_lms_base_url>
# For local deployment the default setting is EDX_API_KEY="PUT_YOUR_API_KEY_HERE"
EDX_API_KEY=<edx_api_key>
```

### For local installation:

IP address in the EDX_LMS_BASE_URL setting must be your private IP address. You can find how to get your private IP 
here: https://www.avg.com/en/signal/find-ip-address. For example, the value may be http://192.168.140.191:18000.  
Note that the private ip can be changed because it is issued by a router, so it will be necessary to change this setting
in the future.

Run loadtests
---

1. export all needed env variables:
```
export APP_KEY=****************
export APP_SECRET=****************
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
