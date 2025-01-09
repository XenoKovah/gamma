"""
Eventually data will be moved away from SQL to Mongo.

This module is intended to be a data schema for all project
entities.
"""

from typing import List
from bson import ObjectId

from django.conf import settings

from schematics.models import Model
from schematics.contrib.mongo import ObjectIdType
from schematics.types import (
    StringType,
    UTCDateTimeType,
    BooleanType,
    ModelType,
    IntType,
    DictType,
)
from schematics.transforms import blacklist

from core.data_models.types import CustomURLType


class UserAction(Model):
    count = IntType(default=0)
    goal = IntType(serialize_when_none=False)
    last = UTCDateTimeType(serialize_when_none=False)

    class Options:
        roles = {
            'public': blacklist('last'),
            'roster': blacklist(''),
            "user": blacklist(''),
        }


class UserBadge(Model):
    badge_uid = StringType(required=False, serialize_when_none=False)
    title = StringType(required=False, serialize_when_none=False)
    description = StringType(required=False, serialize_when_none=False)
    done = BooleanType(default=False)
    progress = DictType(ModelType((UserAction), default={}))
    url = CustomURLType(required=True, relative=settings.STORE_RELATIVE_URLS)

    class Options:
        roles = {
            'public': blacklist(''),
            'roster': blacklist(''),
            "user": blacklist(''),
        }


class DepBadge(Model):
    """
    Dependency badge.
    """

    badge_uid = StringType(required=True)
    badge_title = StringType(required=True)
    url = CustomURLType(required=True, relative=settings.STORE_RELATIVE_URLS)


class Badge(Model):
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    badge_uid = StringType(required=True, serialize_when_none=False)
    slug = StringType(required=False)
    title = StringType(required=False, serialize_when_none=False)
    description = StringType(required=False, serialize_when_none=False)
    url = CustomURLType(required=True, relative=settings.STORE_RELATIVE_URLS)
    rules = ModelType(Rules, serialize_when_none=False)
    active = BooleanType(default=True)

    class Options:
        roles = {
            'public': blacklist('_id'),
            'skeleton': blacklist('rules', '_id', 'active')
        }

    def update_badge(self, data):
        self.import_data(data).validate()

    @property
    def required_badges(self) -> List:
        return self.rules.badges if self.rules else []
