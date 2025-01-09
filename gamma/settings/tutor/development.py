from ..devstack import *



# hardcoded for gammification dashboard and leaderboard to properly use the media urls
STORE_RELATIVE_URLS = False

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

MONGO_URL = "mongodb://mongodb:27017/"
MONGO_DATABASE = "gamma_data"

EDX_LMS_BASE_URL = "http://lms:8000"
EDX_API_KEY = "ktS2WdkPHgwyf4cq8yhujhvx"

CELERY_BROKER_URL = "redis://redis:6379/3"





EDX_LMS_BASE_URL = "http://local.edly.io:8000"

