from os import environ

from ..production import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "rgg",
        "USER": "openedx",
        "PASSWORD": environ.get("DB_PASSWORD", ""),
        "HOST": "mysql",
        "PORT": "3306",
        "OPTIONS": {
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "redis:6379",
        "OPTIONS": {
            'DB': 3,
        },
    }
}

EDX_LMS_BASE_URL = "http://lms:8000"
EDX_API_KEY = environ.get("EDX_API_KEY", "")

CELERY_BROKER_URL = "redis://redis:6379/3"
