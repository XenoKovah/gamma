"""
Settings related to integration with edX platform.
"""

from os import environ


EDX_API_VERSION = "v2"
EDX_API_V2_SUFFIX = f"/api/courses/{EDX_API_VERSION}/gamma/"

EDX_LMS_BASE_URL = environ.get('EDX_LMS_BASE_URL', 'http://localhost:8080')
EDX_API_KEY = environ.get('EDX_LMS_BASE_URL', 'edx_xapi_key')
