from os import path

from .edx_platform import *  # pylint: disable=wildcard-import
from .logging import LOGGING  # pylint: disable=unused-import


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
    'django.contrib.staticfiles',  # required for serving swagger ui's css/js files

    # Django Rest Framework
    'rest_framework',

    # SSO apps
    'social_django',

    # Local apps
    'achievements',
    'avatars',
    'badges',
    'core',
    'courseware',
    'events',
    'googlecharts',
    'leaderboard',
    'rules',
    'users',

    'corsheaders',
    'webpack_loader',
    'drf_yasg',
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GAMIFICATION_BACKENDS = [
    'avatars.backend.AvatarBackend',
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
CELERY_BEAT_SCHEDULE = {
    'update-leaderboard-every-minute': {
        'task': 'leaderboard.tasks.task_update_leaderboards',
        'schedule': 60,
    }
}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": environ.get("REDIS_LOCATION", "redis:6379"),
        "OPTIONS": {
            "DB": environ.get("REDIS_DB", 1),
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
        'BUNDLE_DIR_NAME': 'frontend/gamma/dist/',
        # NOTE: Stats file is not polled when in production (DEBUG=False).
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

LEADERBOARD_INITIALIZATION_BATCH_SIZE = environ.get('LEADERBOARD_INITIALIZATION_BATCH_SIZE', 100)

AUTHENTICATION_BACKENDS = (
    'auth_backends.backends.EdXOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
SOCIAL_AUTH_STRATEGY = 'auth_backends.strategies.EdxDjangoStrategy'
LOGIN_REDIRECT_URL = '/gamma/badges/'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
OAUTH2_PROVIDER_URL = environ.get('OAUTH2_PROVIDER_URL', 'http://localhost:8080/oauth2')
SOCIAL_AUTH_EDX_OAUTH2_KEY = environ.get('SOCIAL_AUTH_EDX_OAUTH2_KEY', 'rgg-key-sso')
SOCIAL_AUTH_EDX_OAUTH2_SECRET = environ.get('SOCIAL_AUTH_EDX_OAUTH2_SECRET', 'rgg-secret-sso')
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = environ.get('SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT', 'http://localhost:8080')
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = environ.get('SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL', 'http://localhost:8080/logout')

SOCIAL_AUTH_PIPELINE = (
    # This first block is a copy of the default pipelines from auth_backends.strategies.EdxDjangoStrategy.
    # We can't import that module here to reference the default set directly (circular dependencies), so we just
    # duplicate it.
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',

    # Gamma-specific pipeline
    'gamma.pipeline.ensure_user_is_synchronized',

    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
