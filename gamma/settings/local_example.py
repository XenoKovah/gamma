from .base import *


# Set these to the correct values for your OAuth2/OpenID Connect provider
SOCIAL_AUTH_EDX_OIDC_KEY = ''
SOCIAL_AUTH_EDX_OIDC_SECRET = ''
SOCIAL_AUTH_EDX_OIDC_URL_ROOT = 'https://lms-domain-name/oauth2'

# This value should be the same as SOCIAL_AUTH_EDX_OIDC_SECRET
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY = SOCIAL_AUTH_EDX_OIDC_SECRET


# For MySQL DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/path/to/my.cnf',
        },
    }
}


# MongoDB configuration
MONGODB_CONF = {
    'HOST': 'localhost',
    'PORT': 27017,
    'USERNAME': None,
    'PASSWORD': None
}
