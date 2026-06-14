from .base import *  # pylint: disable=wildcard-import


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

CELERY_TASK_ALWAYS_EAGER = True

# Off by default in tests so the once-per-day Continuous Learning award does not perturb
# the many existing tests that fire events and assert exact point totals. The feature's
# own tests (users/tests/test_continuous_learning.py) enable it explicitly.
RGG_CONTINUOUS_LEARNING_ENABLED = False

DB_DATA = 'test-data'

ENABLE_CORS_HEADERS = True
CORS_ORIGIN_ALLOW_ALL = True
