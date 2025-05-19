"""
Achievement fields.
"""

import os
from urllib.parse import unquote

from django.db.models import ImageField
from slugify import Slugify


# The class is kept for backward compatibility. It's used in old migrations
# and its deletion can break them.
class CustomImageField(ImageField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_upload_to_value = kwargs['upload_to']
        self.upload_to = self.slugify_file_location(kwargs['upload_to'])

    @staticmethod
    def slugify_file_location(path):
        def wrapper(_, filename):
            slugify = Slugify(separator='_', safe_chars='-./', to_lower=True)
            slugified_filename = slugify(unquote(filename))
            return os.path.join(path, slugified_filename)
        return wrapper

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['upload_to'] = self.initial_upload_to_value
        return name, path, args, kwargs
