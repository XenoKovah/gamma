from os import environ

from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

CELERY_TASK_ALWAYS_EAGER = True

MONGO_DB_NAME = "test-db"
DB_DATA = 'test-data'

ENABLE_CORS_HEADERS = True
CORS_ORIGIN_ALLOW_ALL = True
