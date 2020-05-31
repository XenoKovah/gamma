"""
Module holding push providers Notification data structure.
"""

from bson import ObjectId
from contextlib import contextmanager

from schematics.contrib.mongo import ObjectIdType
from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.types import StringType, DictType, ListType, URLType
from schematics.transforms import blacklist


class BaseOneSignalNotif(Model):
    """
    Base model for OneSignal notification.

    _id is for saving the Notif in db.
    """
    _id = ObjectIdType(
        metadata={'readOnly': True},
        serialize_when_none=False, default=ObjectId
    )
    headings = DictType(StringType(), required=True, serialize_when_none=False)
    contents = DictType(StringType(), required=True, serialize_when_none=False)
    chrome_web_icon = URLType(required=False, serialize_when_none=False)
    url = URLType(required=False, serialize_when_none=False)

    class Options:
        roles = {
            "public": blacklist("_id", "users"),
        }

    def __eq__(self, other):
        return all([
            self.contents == other.contents,
            self.headings == other.headings,
            self.chrome_web_icon == other.chrome_web_icon,
            self.url == other.url,
        ])

class OneSignalNotif(BaseOneSignalNotif):
    """
    Notification for player ids.

    https://documentation.onesignal.com/reference/create-notification#send-to-specific-devices
    """
    include_external_user_ids = ListType(StringType(), required=False, serialize_when_none=False)
    include_player_ids = ListType(StringType(), required=False, serialize_when_none=False)

    class Options:
        roles = {
            "public": blacklist("_id"),
        }

    def __eq__(self, other):
        parent_equality = super().__eq__(other)

        return all([
            parent_equality,
            self.include_external_user_ids == other.include_external_user_ids,
            self.include_player_ids == other.include_player_ids,
        ])

    @classmethod
    def create_by_user_ids(cls, users: list):
        assert isinstance(users, list)

        return cls().import_data({"include_external_user_ids": [user.user_uid for user in users]})

    @classmethod
    def create_by_player_ids(cls, users: list):
        assert isinstance(users, list)

        include_player_ids = []
        for user in users:
            include_player_ids.extend(user.player_ids)

        return cls().import_data({"include_player_ids": include_player_ids})

    def validate_include_external_user_ids(self, data, value):
        """
        include_player_ids will overwrite include_external_user_ids data.
        """
        if data['include_player_ids'] is not None:
            raise ValidationError("Doesn't allow both include_external_user_ids and include_player_ids")
        return value

    @contextmanager
    def as_include_external_user_ids(self, user):
        """
        Including external user_id.
        """
        self.include_external_user_ids = [user.user_uid]

        yield self

        self.include_external_user_ids = None
