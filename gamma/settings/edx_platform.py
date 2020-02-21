"""
Settings related to integration with edX platform.
"""

from os import environ


EDX_API_VERSION = "v0"
EDX_API_V2_SUFFIX = "gamma_bridge/api/{}/".format(EDX_API_VERSION)

EDX_LMS_BASE_URL = environ.get('EDX_LMS_BASE_URL', 'http://localhost:8080')
EDX_API_KEY = environ.get('EDX_API_KEY', 'edx_xapi_key')
