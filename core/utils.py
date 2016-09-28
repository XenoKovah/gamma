import hashlib
from uuid import uuid4

from django.conf import settings


def key_secret_generator():
    """
    Generate a key/secret for AppClient.
    """
    hash = hashlib.sha1(uuid4().hex.encode('utf-8'))
    hash.update(settings.SECRET_KEY.encode('utf-8'))
    return hash.hexdigest()[::2]
