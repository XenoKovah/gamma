"""Guards on the event type enums."""
import pytest

from events.enums import EdxCommonEventTypes, RggInternalEventTypes
from events.models import EventConfiguration

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('event_type', list(RggInternalEventTypes) + list(EdxCommonEventTypes))
def test_event_titles_fit_configuration_column(event_type):
    """
    Every enum title must fit the column the seeding commands store it in.

    Those commands write ``event_type.title`` straight into ``EventConfiguration.title``.
    The suite runs on SQLite, which does not enforce VARCHAR limits, so an over-long
    title passes here and then fails against MySQL as a DataError at deploy time — which
    is exactly how the Continuous Learning weekday event was caught. Assert the limit
    explicitly instead of relying on the backend to notice.
    """
    max_length = EventConfiguration._meta.get_field('title').max_length
    title = str(event_type.title)

    assert len(title) <= max_length, (
        f'{event_type.name} title {title!r} is {len(title)} characters; '
        f'EventConfiguration.title holds {max_length}'
    )
