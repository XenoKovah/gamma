from dataclasses import dataclass


@dataclass
class EventProgress:
    """
    Encapsulate event progress data during update achievement dependencies.
    """

    current: dict
    by_event: dict
    event_name: str
    action: dict
