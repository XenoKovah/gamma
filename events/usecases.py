import logging

from edx_integration.api.v2.utils import get_gamma_events_list
from events.entity import ExternalEvent, SystemEvent


log = logging.getLogger(__name__)


class ProcessIncomingEventUseCase:
    """
    Use case for processing an incoming external event.
    """

    def __init__(self, event_repository):
        self.repository = event_repository

    def execute(self, data: dict, *args, **kwargs) -> ExternalEvent:
        external_event = ExternalEvent(data, strict=False)
        return self.repository.save(external_event)


class GetEventsUseCase:
    """
    Use case for retrieving events.
    """

    def __init__(self, event_repository):
        self.repository = event_repository

    def execute(self, public: bool = False, *args, **kwargs) -> list:
        return self.repository.read(public)


class UpdateEventUseCase:
    """
    Use case for updating an existing system event.
    """

    def __init__(self, event_repository):
        self.repository = event_repository

    def execute(self, event_data: dict, *args, **kwargs) -> None:
        event = SystemEvent(event_data)
        self.repository.update(event)


class GetExternalEventUseCase:
    """
    Use case for converting raw data to an ExternalEvent entity.
    """

    def __init__(self, event_repository):
        self.repository = event_repository

    def execute(self, event: dict, *args, **kwargs) -> ExternalEvent:
        return self.repository.convert_to_external_event(event)


class CreateOrUpdateEventConfigUseCase:

    def __init__(self, event_repository):
        self.repository = event_repository

    def execute(self, event: dict, *args, **kwargs) -> ExternalEvent:

        UpdateEventUseCase(self.repository).execute({
            "event_type": event.event_type,
            "title": event.title,
            "award": event.award,
            "color": event.color,
        })

        # When changing event title in PostgreSQL DB, it is necessary to change
        # this event title in Mongo DB for each user who has this event in the "chart".
        self.repository.db.users.update_event_title_in_charts(event.event_type, event.title)


class PoppulateEventsUseCase:

    def __init__(self, event_repository):
        self.repository = event_repository

    def execute(self):
        events_list = get_gamma_events_list()

        if not events_list:
            return None, None

        events_specified = self.repository.get_events_config_types()

        events_choices = (
            (e['event_type'], e['event_type']) for e in events_list if e['event_type'] not in events_specified
        )
        data_event_names = {
            e['event_type']: e['verbose_name'] for e in events_list if e['event_type'] not in events_specified
        }
        return events_choices, data_event_names


class CreateUpdateEventConfig:

    def __init__(self, event_repository):
        self.repository = event_repository

    def execute(self, data):
        event, _ = self.repository.update_or_create_event(data)

        UpdateEventUseCase(self.repository).execute({
            "event_type": event.event_type,
            "title": event.title,
            "award": event.award,
            "color": event.color,
        })

        # Should be moved to users user usecases.
        self.repository.db.users.update_many(
            {f'chart.{event.event_type}': {'$exists': True}},
            {'$set': {f"chart.{event.title}.title": event.title}},
        )

        return event
