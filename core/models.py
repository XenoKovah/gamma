import re
import hashlib
from uuid import uuid4

from django.db import models
from django.conf import settings

from core.data_models.models import AppClient as AppClientModel
from core import db


def key_secret_generator():
    """
    Generate a key/secret for AppClient.
    """
    _hash = hashlib.sha1(uuid4().hex.encode('utf-8'))
    _hash.update(settings.SECRET_KEY.encode('utf-8'))
    return _hash.hexdigest()[::2]


def mongo_compatible(value):
    """
    Validate the value to be compatible with mondo naming.
    """
    return re.match(r"^[\da-z]+$", value)


class AppClient(models.Model):
    """
    Client application models to hold KEY and SECRET.
    """

    name = models.CharField(max_length=32, unique=True, validators=[mongo_compatible])
    key = models.CharField(max_length=32, unique=True, db_index=True, default=key_secret_generator)
    secret = models.CharField(max_length=32, unique=True, default=key_secret_generator)

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        super(AppClient, self).save(*args, **kwargs)  # pylint: disable=super-with-arguments
        db.clients.update_one(AppClientModel({
            "uid": self.name,
            "key": self.key,
            "secret": self.secret}))
