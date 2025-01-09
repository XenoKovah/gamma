"""
This module defines data schemas for Event entities using the Schematics library.
"""

from datetime import datetime

from bson import ObjectId

from schematics.models import Model
from schematics.contrib.mongo import ObjectIdType
from schematics.types import StringType, UTCDateTimeType, IntType
from schematics.transforms import blacklist


class ExternalEvent(Model):
    """
    Schema for incoming API request data related to events.
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
    Schema for accepted events stored in the system.
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

    def add_to_rules(self, rule, value):
        rule.add_action(self, value)
    

class Rule:
    events = []

    def add_action(self, ):
        """"""
