import logging
from pymongo import WriteConcern
from schematics.exceptions import DataError
from typing import Optional, List, Union

from events.entity import SystemEvent, ExternalEvent
from events.exceptions import (
    EventTypeIsNotRecognizableError,
    DuplicatedEventOccursError,
    EventDataIsNotCorrectError,
)
from events.models import Event


log = logging.getLogger(__name__)


class EventRepository:
    """
    Repository class to manage events in the database.

    Handles conversion, validation, and database operations for events.
    """

    def __init__(self, db):
        self.db = db

    def convert_to_external_event(self, data: dict) -> ExternalEvent:
        try:
            return ExternalEvent(data, strict=False)
        except DataError as ex:
            log.error(f"Cannot convert to ExternalEvent: {ex}")
            raise

    def convert_to_event(self, data: dict) -> SystemEvent:
        try:
            return SystemEvent(data, strict=False)
        except DataError as ex:
            log.error(f"Cannot convert to SystemEvent: {ex}")
            raise

    def find_by_type(self, event_type: str) -> Optional[SystemEvent]:
        if data := self.db.events.find_one({"event_type": event_type}):
            return self.convert_to_event(data)
        return None

    def update(self, event: SystemEvent) -> None:
        data = event.to_native()
        data.pop("_id", None)

        self.db.events.update_one({"event_type": event.event_type}, {"$set": data}, upsert=True)

    def read(self, public: bool = False) -> List[Union[SystemEvent, dict]]:
        return [
            self.convert_to_event(event).to_primitive("public") if public else self.convert_to_event(event)
            for event in self.db.events.find()
        ]

    def save(self, event: ExternalEvent) -> ExternalEvent:
        try:
            event.validate()
        except DataError:
            raise EventDataIsNotCorrectError("Event data is not correct")

        if not (system_event := self.find_by_type(event.event_type)):
            raise EventTypeIsNotRecognizableError("Event type is not recognizable")

        if self.db.event_history.find_one({"uid": event.uid, "user_uid": event.username, "client": event.client}):
            raise DuplicatedEventOccursError("Repeated event occurs")

        event.points = system_event.award
        event.title = system_event.title

        self.db.event_history.with_options(write_concern=WriteConcern(w=0)).insert_one(event.to_native())

        return event

    def get_events_config_types(self):
        return Event.objects.all().values_list('event_type', flat=True)

    def update_or_create_event(self, event):
        event_type = event.pop('event_type')
        return Event.objects.update_or_create(event_type=event_type, defaults=event)
