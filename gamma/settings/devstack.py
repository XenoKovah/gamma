from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

CORS_ORIGIN_ALLOW_ALL = True

WEBPACK_LOADER['DEFAULT'].update({
    'CACHE': not DEBUG,
    'STATS_FILE': path.join(ROOT_DIR, 'webpack-stats-dev.json')
})
