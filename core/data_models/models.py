"""
Eventually data will be moved away from SQL to Mongo.


This module is intended to be a data schema for all project
entities.
"""

from typing import List
from datetime import datetime
from bson import ObjectId

from django.conf import settings

from schematics.models import Model
from schematics.contrib.mongo import ObjectIdType
from schematics.types import (
    StringType,
    UTCDateTimeType,
    ListType, BooleanType,
    ModelType,
    IntType,
    DictType,
)
from schematics.transforms import blacklist, whitelist

from core.data_models.types import CustomURLType


class EventModel(Model):
    """
    Incomming API request model.
    """
    uid = StringType(required=True)
    signup_source = StringType(required=False)
    username = StringType(required=True, serialized_name='user_uid')
    event_type = StringType(required=True)
    org = StringType()
    course_id = StringType()
    title = StringType(required=False)
    points = IntType()
    date = UTCDateTimeType(metadata={'readOnly': True}, default=datetime.now)
    client = StringType()

    class Options:
        roles = {
            'public': blacklist(''),
        }


class SystemEvent(Model):
    """
    Accepted Events.
    """
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    event_type = StringType(required=True)
    title = StringType(required=True)
    award = IntType()
    color = StringType(required=True)

    class Options:
        roles = {
            'public': blacklist('_id'),
        }


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


class Status(Model):
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    status_uid = StringType(required=True)
    slug = StringType(required=True)
    title = StringType(required=True)
    description = StringType(required=False)
    active = BooleanType(default=False)
    points = IntType(serialized_name='status_points')
    progress = IntType(serialize_when_none=False)
    color = StringType(serialize_when_none=False)
    url = CustomURLType(serialize_when_none=False, relative=settings.STORE_RELATIVE_URLS)

    def __hash__(self):
        return hash(self.status_uid)

    class Options:
        roles = {
            'public': blacklist('_id'),
            'client': blacklist('_id', 'active'),
            "user": blacklist('_id', 'active'),
        }

    def __lt__(self, value):
        return self.points < value.points

    def __gt__(self, value):
        return self.points > value.points


class UserStatus(Model):
    status_uid = StringType(required=True)
    status_title = StringType(required=True)
    url = CustomURLType(required=True, relative=settings.STORE_RELATIVE_URLS)

    class Options:
        roles = {
            'public': blacklist('')
        }


class DailyProgress(Model):
    date = UTCDateTimeType(required=True)
    points = IntType(required=True, default=0)

    class Options:
        roles = {
            'public': blacklist(''),
            "user": blacklist(''),
        }


class UserEventPoints(Model):
    title = StringType(required=False)
    points = IntType(required=True, default=0)

    class Options:
        roles = {
            'public': blacklist(''),
            "user": blacklist(''),
        }


class DepBadge(Model):
    """
    Dependency badge.
    """
    badge_uid = StringType(required=True)
    badge_title = StringType(required=True)
    url = CustomURLType(required=True, relative=settings.STORE_RELATIVE_URLS)


class SystemAction(Model):
    name = StringType(required=True)
    goal = IntType(required=True)


class Interval(Model):
    start = UTCDateTimeType(required=True)
    end = UTCDateTimeType(required=True)

    class Options:
        roles = {
            'public': blacklist(''),
        }


class Filters(Model):
    interval = ModelType(Interval, serialize_when_none=False)
    org = StringType(min_length=1, serialize_when_none=False)
    frequency = IntType(serialize_when_none=False)
    course = StringType(min_length=1, serialize_when_none=False)

    class Options:
        roles = {
            'public': blacklist(''),
        }


class Rules(Model):
    actions = DictType(IntType(), serialize_when_none=False, default={})
    badges = ListType(StringType(), serialize_when_none=False, default=[])
    status_badge = StringType(min_length=1, serialize_when_none=False)
    filters = ModelType(Filters, serialize_when_none=False)

    class Options:
        roles = {
            'public': blacklist(''),
        }

    def __bool__(self):
        """
        Evaluates Rules to bool.

        Returns True if any of the valid rules is
        presented.
        """
        return any((self.get("actions"),
                    self.get("badges"),
                    self.get("status_badge")))


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


class User(Model):
    """
    Game profile data model.
    """
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    user_uid = StringType(required=True)
    username = StringType(serialize_when_none=False)
    signup_source = StringType(required=False)
    points = IntType(default=0)
    badges = DictType(ModelType(UserBadge), default={})
    system_badges = ListType(ModelType(Badge), default=[])
    statuses = ListType(ModelType(Status), default=[])
    system_statuses = ListType(ModelType(Status), default=[])
    system_events = ListType(ModelType(SystemEvent), default=[])
    chart = DictType(ModelType(UserEventPoints), default={})
    progress = DictType(ListType(ModelType(DailyProgress)), default={})
    player_ids = ListType(StringType(), serialize_when_none=False, required=False)

    class Options:
        roles = {
            'public': blacklist('_id', 'user_uid', 'player_ids'),
            'roster': blacklist('_id', 'system_badges', 'statuses', 'chart', 'progress', 'player_ids'),
            "user": blacklist('system_badges', 'system_statuses'),
        }

    def get_player_ids(self):
        return self.player_ids

    @property
    def achieved_badges(self):
        return [badge for badge in self.badges if self.badges[badge].done]

    def filter_done(self):
        """
        Filter Badges to return only achieved ones.
        """

        if not self.get('badges'):
            return

        self.badges = {
            badge: self.badges[badge]
            for badge in self.badges if self.badges[badge].done}

    def has_status(self, status_uid) -> bool:
        return status_uid in [_.status_uid for _ in self.statuses]


class Leaders(Model):
    """
    Leaderboard data model.

    List of User models.
    """
    roster = ListType(ModelType(User), default=[])

    class Options:
        roles = {
            'public': blacklist(''),
            'roster': blacklist(''),
        }

    def to_primitive(self, role=None, app_data=None, **kwargs):
        """
        Adding filtering for User badges.
        """

        for user in self.roster:
            user.filter_done()

        return super().to_primitive(role=role, app_data=app_data, **kwargs)


class AppClient(Model):
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    uid = StringType(required=True)
    key = StringType(required=True)
    secret = StringType(required=True)

    class Options:
        roles = {
            'public': blacklist('_id', 'key', 'secret'),
            'internal': blacklist('_id')
        }
