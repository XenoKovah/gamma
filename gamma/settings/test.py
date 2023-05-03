from os import environ  # pylint: disable=unused-import

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

EDX_NOTIFICATION_API_SUFFIX = "notifications/api/v0/send-notification/"
EDX_NOTIFICATION_ENABLED = True
ONESIGNAL_NOTIFICATION_ENABLED = True
