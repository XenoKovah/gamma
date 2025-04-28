from os import environ

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from .base import *  # pylint: disable=unused-import, wildcard-import


sentry_sdk.init(
    dsn=f"{environ.get('SENTRY_DSN', '')}",
    environment=f"{environ.get('SENTRY_ENV', '')}",
    server_name=f"{environ.get('SENTRY_SERVER_NAME', '')}",
    release=f"{environ.get('SENTRY_RELEASE', '')}",
    integrations=[DjangoIntegration(), CeleryIntegration()]
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

CORS_ORIGIN_ALLOW_ALL = True

WEBPACK_LOADER['DEFAULT'].update({
    'CACHE': not DEBUG,
    'STATS_FILE': path.join(ROOT_DIR, 'frontend', 'gamma', 'webpack-stats-dev.json')
})

SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
