"""
Eventually data will be moved away from SQL to Mongo.


This module is intended to be a data schema for all project
entities.
"""
from datetime import datetime
from bson import ObjectId

from schematics.models import Model
from schematics.contrib.mongo import ObjectIdType
from schematics.types import (
    StringType,
    UTCDateTimeType,
    ListType, BooleanType,
    URLType,
    ModelType,
    IntType,
    DictType,
    DateType
)
from schematics.transforms import blacklist, whitelist


class EventModel(Model):
    """
    Incomming API request model.
    """
    uid = StringType(required=True)
    username = StringType(required=True, serialized_name='user_uid')
    event_type = StringType(required=True)
    org = StringType()
    course_id = StringType()
    points = IntType()
    date = UTCDateTimeType(metadata={'readOnly': True}, default=datetime.now)
    client = StringType()

    class Options:
        roles = {
            'public': blacklist("_id"),
        }


class SystemEvent(Model):
    """
    Accepted Events.
    """
    event_type = StringType(required=True)
    title = StringType(required=True)
    award = IntType()
    color = StringType(required=True)


class UserAction(Model):
    count = IntType(default=0)
    goal = IntType()
    last = UTCDateTimeType()

    class Options:
        roles = {
            'public': blacklist('last'),
            'roster': blacklist(''),
        }


class UserBadge(Model):
    badge_uid = StringType(required=False)
    badge_title = StringType(required=False)
    done = BooleanType(default=False)
    progress = DictType(ModelType((UserAction), default={}))
    url = URLType(required=True)

    class Options:
        roles = {
            'public': blacklist(''),
            'roster': blacklist(''),
        }


class Status(Model):
    status_uid = StringType(required=True)
    slug = StringType(required=True)
    title = StringType(required=True)
    active = BooleanType(default=False)
    points = IntType(serialized_name='status_points')
    progress = IntType()
    color = StringType()
    url = URLType()

    def __hash__(self):
        return hash(self.status_uid)

    class Options:
        roles = {
            'public': blacklist(''),
            'client': blacklist('active')
        }

    def __lt__(self, value):
        return self.points < value.points

    def __gt__(self, value):
        return self.points > value.points

class UserStatus(Model):
    status_uid = StringType(required=True)
    status_title = StringType(required=True)
    url = URLType(required=True)

    class Options:
        roles = {
            'public': blacklist('')
        }


class DailyProgress(Model):
    date = DateType(required=True)
    points = IntType(required=True, default=0)

    class Options:
        roles = {
            'public': blacklist('')
        }


class UserEventPoints(Model):
    points = IntType(required=True, default=0)

    class Options:
        roles = {
            'public': blacklist('')
        }


class User(Model):
    """
    Game profile data model.
    """
    user_uid = StringType(required=True)
    username = StringType()
    points = IntType(default=0)
    badges = DictType(ModelType(UserBadge), default={})
    statuses = ListType(ModelType(Status), default=[])
    chart = DictType(ModelType(UserEventPoints), default={})
    progress = DictType(ListType(ModelType(DailyProgress)), default={})

    class Options:
        roles = {
            'public': blacklist('user_uid'),
            'roster': whitelist('username', 'user_uid', 'badges'),
        }

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

class DepBadge(Model):
    """
    Dependency badge.
    """
    badge_uid = StringType(required=True)
    badge_title = StringType(required=True)
    url = URLType(required=True)

class SystemAction(Model):
    name = StringType(required=True)
    goal = IntType(required=True)


class Interval(Model):
    start = UTCDateTimeType(required=True)
    end = UTCDateTimeType(required=True)


class Filters(Model):
    interval = ModelType(Interval)
    org = StringType()
    frequency = IntType()
    course = StringType()


class Rules(Model):
    actions = DictType(IntType(), default={})
    badges = ListType(StringType(), default=[])
    status_badge = StringType()
    filters = ModelType(Filters)


class Badge(Model):
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    badge_uid = StringType(required=True)
    slug = StringType(required=True)
    title = StringType()
    badge_title = StringType(required=True)
    url = URLType(required=True)
    rules = ModelType(Rules)
    active = BooleanType(default=False)

    class Options:
        roles = {
            'public': blacklist(''),
            'skeleton': blacklist('rules', '_id')
        }

    def update_badge(self, data):
        self.import_data(data)


class AppClient(Model):
    uid = StringType(required=True)
    key = StringType(required=True)
    secret = StringType(required=True)

    class Options:
        roles = {
            'public': blacklist('key', 'secret'),
            'internal': blacklist('')
        }
