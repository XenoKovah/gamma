from .base import *


# MongoDB configuration
MONGODB_CONF = {
    'HOST': 'mongo',
    'PORT': 27017,
    'USERNAME': None,
    'PASSWORD': None
}


ENABLE_CORS_HEADERS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'google.com',
    'hostname.example.com',
    'localhost:8000',
    '127.0.0.1:9000'
)

EDX_LMS_BASE_URL = "provide_edx_lms_base_url"
EDX_API_KEY = "provide_edx_api_key"
