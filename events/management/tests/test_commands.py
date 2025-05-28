import pytest
from django.core.management import call_command

from events.enums import EdxCommonEventTypes, RggInternalEventTypes
from events.models import EventType, EventConfiguration


@pytest.mark.no_rgg_events
@pytest.mark.django_db
def test_initialize_rgg_internal_events_non_existing():
    call_command('initialize_rgg_internal_events')

    for enum_item in RggInternalEventTypes:
        event_type = EventType.objects.get(name=enum_item.value)
        event_configuration = EventConfiguration.objects.get(event_type=event_type)

        assert event_type is not None
        assert event_type.name == enum_item.value
        assert event_configuration.award == 0

    assert EventType.objects.count() == len(RggInternalEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(RggInternalEventTypes.get_all())


@pytest.mark.no_rgg_events
@pytest.mark.django_db
def test_initialize_rgg_internal_events_does_not_duplicate_existing_event_type_and_configuration(
    event_type_factory, event_configuration_factory
):
    enum_item = RggInternalEventTypes.get_all()[0]
    event_type = event_type_factory(name=enum_item)
    event_configuration_factory(event_type=event_type, title='Test Title', award=0)

    assert EventType.objects.count() == 1
    assert EventConfiguration.objects.count() == 1

    call_command('initialize_rgg_internal_events')

    for enum_item in RggInternalEventTypes:
        event_type = EventType.objects.get(name=enum_item.value)
        event_configuration = EventConfiguration.objects.get(event_type=event_type)

        assert event_type is not None
        assert event_type.name == enum_item.value
        assert event_configuration.award == 0

    assert EventType.objects.count() == len(RggInternalEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(RggInternalEventTypes.get_all())


@pytest.mark.no_rgg_events
@pytest.mark.django_db
def test_initialize_rgg_internal_events_reset_award_to_zero(
    event_type_factory, event_configuration_factory
):
    enum_item = RggInternalEventTypes.get_all()[0]
    event_type = event_type_factory(name=enum_item)
    event_configuration = event_configuration_factory(event_type=event_type, title='Test Title', award=100)

    assert EventType.objects.count() == 1
    assert EventConfiguration.objects.count() == 1
    assert event_configuration.award == 100

    call_command('initialize_rgg_internal_events')

    for enum_item in RggInternalEventTypes:
        event_type = EventType.objects.get(name=enum_item.value)
        event_configuration = EventConfiguration.objects.get(event_type=event_type)

        assert event_type is not None
        assert event_type.name == enum_item.value
        assert event_configuration.award == 0

    assert EventType.objects.count() == len(RggInternalEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(RggInternalEventTypes.get_all())


@pytest.mark.no_rgg_events
@pytest.mark.django_db
def test_initialize_edx_common_events_non_existing():
    call_command('initialize_edx_common_events')

    for enum_item in EdxCommonEventTypes:
        event_type = EventType.objects.get(name=enum_item.value)
        event_configuration = EventConfiguration.objects.get(event_type=event_type)

        assert event_type.name == enum_item.value
        assert event_configuration.title == enum_item.title
        assert event_configuration.award == enum_item.award

    assert EventType.objects.count() == len(EdxCommonEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(EdxCommonEventTypes.get_all())


@pytest.mark.no_rgg_events
@pytest.mark.django_db
def test_initialize_edx_common_events_does_not_duplicate_existing_event_type_and_configuration(
    event_type_factory, event_configuration_factory
):
    for enum_item in EdxCommonEventTypes:
        event_type = event_type_factory(name=enum_item.value)
        event_configuration_factory(event_type=event_type, title=enum_item.title)

    assert EventType.objects.count() == len(EdxCommonEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(EdxCommonEventTypes.get_all())

    call_command('initialize_edx_common_events')

    for enum_item in EdxCommonEventTypes:
        event_type = EventType.objects.get(name=enum_item.value)
        event_configuration = EventConfiguration.objects.get(event_type=event_type)

        assert event_type.name == enum_item.value
        assert event_configuration.title == enum_item.title

    assert EventType.objects.count() == len(EdxCommonEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(EdxCommonEventTypes.get_all())


@pytest.mark.no_rgg_events
@pytest.mark.django_db
def test_initialize_edx_common_events_not_reset_existent_award_and_title(
    event_type_factory, event_configuration_factory
):
    for counter, enum_item in enumerate(EdxCommonEventTypes):
        event_type = event_type_factory(name=enum_item.value)
        event_configuration = event_configuration_factory(
            event_type=event_type, award=100, title=f'test_title_{counter}'
        )

        assert event_configuration.award == 100
        assert event_configuration.title == f'test_title_{counter}'

    assert EventType.objects.count() == len(EdxCommonEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(EdxCommonEventTypes.get_all())

    call_command('initialize_edx_common_events')

    for counter, enum_item in enumerate(EdxCommonEventTypes):
        event_type = EventType.objects.get(name=enum_item.value)
        event_configuration = EventConfiguration.objects.get(event_type=event_type)

        assert event_type.name == enum_item.value
        assert event_configuration.title == f'test_title_{counter}'
        assert event_configuration.award == 100

    assert EventType.objects.count() == len(EdxCommonEventTypes.get_all())
    assert EventConfiguration.objects.count() == len(EdxCommonEventTypes.get_all())
