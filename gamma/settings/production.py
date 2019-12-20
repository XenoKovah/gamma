from .base import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

WEBPACK_LOADER['DEFAULT'].update({
    'CACHE': not DEBUG,
    'STATS_FILE': path.join(ROOT_DIR, 'webpack-stats-prod.json')
})
