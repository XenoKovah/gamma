import pytest
from django.core.management import call_command

from events.enums import EdxCommonEventTypes
from events.models import EventConfiguration, EventType


@pytest.mark.django_db
def test_initialize_creates_done_toggled_configuration():
    call_command('initialize_edx_common_events')

    configuration = EventConfiguration.objects.get(event_type__name='edx_done_toggled')
    assert configuration.award == 5
    assert configuration.title == 'Mark a Unit as Complete'


@pytest.mark.django_db
def test_initialize_is_idempotent_and_covers_all_common_events():
    call_command('initialize_edx_common_events')
    call_command('initialize_edx_common_events')

    common_names = {event.value for event in EdxCommonEventTypes}
    assert EventType.objects.filter(name__in=common_names).count() == len(common_names)
    assert EventConfiguration.objects.filter(event_type__name__in=common_names).count() == len(common_names)


@pytest.mark.django_db
def test_initialize_does_not_clobber_admin_tuned_awards():
    call_command('initialize_edx_common_events')
    configuration = EventConfiguration.objects.get(event_type__name='edx_done_toggled')
    configuration.award = 7
    configuration.save(update_fields=('award',))

    call_command('initialize_edx_common_events')

    configuration.refresh_from_db()
    assert configuration.award == 7
