from .base import *  # pylint: disable=wildcard-import


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

CELERY_TASK_ALWAYS_EAGER = True

DB_DATA = 'test-data'

ENABLE_CORS_HEADERS = True
CORS_ORIGIN_ALLOW_ALL = True
