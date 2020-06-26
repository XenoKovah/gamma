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
    title = StringType(required=False)
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
    date = UTCDateTimeType(required=True)
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

    class Options:
        roles = {
            'public': blacklist(''),
        }


class Filters(Model):
    interval = ModelType(Interval)
    org = StringType()
    frequency = IntType()
    course = StringType()

    class Options:
        roles = {
            'public': blacklist(''),
        }


class Rules(Model):
    actions = DictType(IntType(), default={})
    badges = ListType(StringType(), default=[])
    status_badge = StringType()
    filters = ModelType(Filters)

    class Options:
        roles = {
            'public': blacklist(''),
        }


class Badge(Model):
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    badge_uid = StringType(required=True, serialize_when_none=False)
    slug = StringType(required=True)
    title = StringType(required=True, serialize_when_none=False)
    url = URLType(required=True)
    rules = ModelType(Rules)
    active = BooleanType(default=True)

    class Options:
        roles = {
            'public': blacklist('_id'),
            'skeleton': blacklist('rules', '_id')
        }

    def update_badge(self, data):
        self.import_data(data)


class User(Model):
    """
    Game profile data model.
    """
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    user_uid = StringType(required=True)
    username = StringType()
    points = IntType(default=0)
    badges = DictType(ModelType(UserBadge), default={})
    system_badges = ListType(ModelType(Badge), default=[])
    statuses = ListType(ModelType(Status), default=[])
    system_statuses = ListType(ModelType(Status), default=[])
    chart = DictType(ModelType(UserEventPoints), default={})
    progress = DictType(ListType(ModelType(DailyProgress)), default={})
    player_ids = ListType(StringType(), required=False)

    class Options:
        roles = {
            'public': blacklist('_id', 'user_uid', 'player_ids'),
            'roster': whitelist('points', 'username', 'user_uid', 'badges'),
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
    uid = StringType(required=True)
    key = StringType(required=True)
    secret = StringType(required=True)

    class Options:
        roles = {
            'public': blacklist('key', 'secret'),
            'internal': blacklist('')
        }
