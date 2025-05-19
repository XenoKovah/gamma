from ..devstack import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "rgg",
        "USER": "openedx",
        "PASSWORD": "wFuscBhG",
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

EDX_API_KEY = "ktS2WdkPHgwyf4cq8yhujhvx"

CELERY_BROKER_URL = "redis://redis:6379/3"

EDX_LMS_BASE_URL = "http://local.edly.io:8000"

OAUTH2_PROVIDER_URL = "http://local.edly.io:8000/oauth2"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://local.edly.io:8000"
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = "http://local.edly.io:8000/logout"
