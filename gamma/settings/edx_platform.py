"""
Settings related to integration with edX platform.
"""

from os import environ
from distutils.util import strtobool


EDX_API_VERSION = "v0"
EDX_API_V2_SUFFIX = f"gamma_bridge/api/{EDX_API_VERSION}/"

EDX_LMS_BASE_URL = environ.get('EDX_LMS_BASE_URL', 'http://localhost:8080')
EDX_API_KEY = environ.get('EDX_API_KEY', 'edx_xapi_key')

EDX_NOTIFICATION_API_SUFFIX  = environ.get('EDX_NOTIFICATION_API_SUFFIX', "notifications/api/v0/send-notification/")
EDX_NOTIFICATION_ENABLED     = strtobool(environ.get('EDX_NOTIFICATION_ENABLED', 'False'))
