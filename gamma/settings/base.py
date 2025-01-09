import os
from os import environ, path
from distutils.util import strtobool

from django.utils.translation import ugettext_lazy as _

from .edx_platform import *  # pylint: disable=wildcard-import


BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
ROOT_DIR = path.dirname(BASE_DIR)

SECRET_KEY = environ.get('SECRET_KEY', 'xhs78m@(e)58)&s8)3r(2s+x=jq(p$hdqqnz-ta5)l=#1g*5ju')


ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django Rest Framework
    'rest_framework',

    # Local apps
    'users',
    'core',
    'achievements',
    'api',
    'googlecharts',

    'corsheaders',

    'webpack_loader',
    'events',
    'rules',

    'badges',
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GAMIFICATION_BACKENDS = [
    'badges.backend.BadgeBackend'
]


SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gamma.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'gamma.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('zh-cn', _('Chinese (China)')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

STATIC_URL = '/static/'
STATIC_ROOT = path.join(BASE_DIR, 'static')


STATICFILES_DIRS = (
    path.join(ROOT_DIR, 'frontend'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# IFrame setting for loading main dashboard in IFrame
X_FRAME_OPTIONS = "SAMEORIGIN"


DB_DATA = 'data'


MEDIA_ROOT = path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Celery settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_DEFAULT_QUEUE = 'gamma'
CELERY_DEFAULT_EXCHANGE = 'gamma'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'gamma'
CELERY_QUEUES = {'gamma': {}}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "redis:6379",
        "OPTIONS": {
            'DB': 1,
        },
    }
}


ENABLE_CORS_HEADERS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:8080',
    'http://localhost:9000',
]


DB_OVERRIDES = dict(
    PASSWORD=environ.get('DB_PASSWORD', DATABASES['default']['PASSWORD']),
    ENGINE=environ.get('DB_ENGINE', DATABASES['default']['ENGINE']),
    USER=environ.get('DB_USER', DATABASES['default']['USER']),
    NAME=environ.get('DB_NAME', DATABASES['default']['NAME']),
    HOST=environ.get('DB_HOST', DATABASES['default']['HOST']),
    PORT=environ.get('DB_PORT', DATABASES['default']['PORT']),
)


for override, value in DB_OVERRIDES.items():
    DATABASES['default'][override] = value


CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL', 'amqp://guest@rabbit')
CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379')


CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": environ.get('REDIS_LOCATION', 'redis:6379'),
        "OPTIONS": {
            'DB': environ.get('REDIS_DB', 1),
        },
    }
}
# Cache time to live is 2 hours.
CACHE_TTL = environ.get('CACHE_TTL', 60 * 60 * 2)

# Set up the name of the main site. By default, the main site is named "main".
MAIN_SIGNUP_SOURCE = environ.get('MAIN_SIGNUP_SOURCE', 'main')

# Ref.: https://github.com/owais/django-webpack-loader#default-configuration
# Define 'STATS_FILE' for each environment in its settings file.
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'webpack_bundles/',  # Use a relative path; must end with slash
        # NOTE: Stats file is not polled when in production (DEBUG=False).
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

STORE_RELATIVE_URLS            = strtobool(environ.get('STORE_RELATIVE_URLS', 'True'))
ONESIGNAL_NOTIFICATION_ENABLED = strtobool(environ.get('ONESIGNAL_NOTIFICATION_ENABLED', 'False'))

EDX_NOTIF_FORMAT_FUNC = environ.get('EDX_NOTIF_FORMAT_FUNC', 'core.notif.formatters.json_formatter')
