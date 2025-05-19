import hashlib
from uuid import uuid4

from django.conf import settings
from django.db import models


def key_secret_generator():
    """
    Generate a key/secret for AppClient.
    """
    _hash = hashlib.sha1(uuid4().hex.encode('utf-8'))
    _hash.update(settings.SECRET_KEY.encode('utf-8'))
    return _hash.hexdigest()[::2]


class AppClient(models.Model):
    """
    Client application models to hold KEY and SECRET.
    """

    name = models.CharField(max_length=32, unique=True)
    key = models.CharField(max_length=32, unique=True, db_index=True, default=key_secret_generator)
    secret = models.CharField(max_length=32, unique=True, default=key_secret_generator)
