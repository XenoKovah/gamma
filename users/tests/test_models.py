import pytest
from datetime import datetime
from typing import Type
from unittest.mock import Mock, patch

import factory
from django.db.models import signals

from events.factories import EventConfigurationFactory, EventFactory
from users.factories import GammaUserCoursePointsFactory, GammaUserFactory
from users.models import GammaUserCoursePoints


@pytest.mark.django_db
def test_update_user_progress(gamma_user_factory: GammaUserFactory) -> None:
    """
    Test the `update_user_progress` class method.
    """
    gamma_user = gamma_user_factory()
    event_points = 10

    gamma_user.update_user_progress(event_points=event_points)

    gamma_user.refresh_from_db()

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    year = str(date.year)
    formatted_date = date.isoformat()

    assert gamma_user.progress[year][0]['date'] == formatted_date
    assert gamma_user.progress[year][0]['points'] == event_points


@pytest.mark.django_db
def test_update_user_chart(
    gamma_user_factory: GammaUserFactory,
    event_configuration_factory: EventConfigurationFactory,
) -> None:
    """
    Test the `update_user_chart` class method.
    """
    gamma_user = gamma_user_factory()
    configuration = event_configuration_factory()

    gamma_user.update_user_chart(configuration)

    gamma_user.refresh_from_db()

    event_chart_key = configuration.event_type.name

    assert gamma_user.chart[event_chart_key]['points'] == configuration.award
    assert gamma_user.chart[event_chart_key]['title'] == configuration.title


@pytest.mark.django_db
def test_update_user_points(gamma_user_factory) -> None:
    """
    Test the `update_user_points` class method.
    """
    gamma_user = gamma_user_factory()
    gamma_user_points = gamma_user.points
    points_to_add = 50
    total_points = gamma_user_points + points_to_add

    gamma_user.update_user_points(points=points_to_add)

    gamma_user.refresh_from_db()

    assert gamma_user.points == total_points


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
def test_update_user_course_points_creates_gamma_user_course_points_record_if_it_does_not_exist(
    gamma_user_factory: Type[GammaUserFactory],
    event_factory: Type[EventFactory],
    event_configuration_factory: Type[EventConfigurationFactory],
) -> None:
    award = 16
    gamma_user = gamma_user_factory()
    event_configuration = event_configuration_factory(award=award)
    event = event_factory(configuration=event_configuration, username=gamma_user.user_uid)

    assert not GammaUserCoursePoints.objects.filter(gamma_user=gamma_user, course_id=event.course_id).exists()

    gamma_user.update_user_course_points(event)

    assert GammaUserCoursePoints.objects.get(gamma_user=gamma_user, course_id=event.course_id).points == award


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
def test_update_user_course_points_increments_gamma_user_course_points_record_if_it_exists(
    gamma_user_factory: Type[GammaUserFactory],
    gamma_user_course_points_factory: Type[GammaUserCoursePointsFactory],
    event_factory: Type[EventFactory],
    event_configuration_factory: Type[EventConfigurationFactory],
) -> None:
    gamma_user = gamma_user_factory()
    gamma_user_course_points = gamma_user_course_points_factory(gamma_user=gamma_user, points=70)
    event_configuration = event_configuration_factory(award=16)
    event = event_factory(
        configuration=event_configuration,
        username=gamma_user.user_uid,
        course_id=gamma_user_course_points.course_id,
    )
    expected_incremented_points_count = 86

    gamma_user.update_user_course_points(event)

    gamma_user_course_points.refresh_from_db()

    assert gamma_user_course_points.points == expected_incremented_points_count


@pytest.mark.django_db
def test_update_user_course_points_does_not_increment_another_gamma_user_course_points_record(
    gamma_user_factory: Type[GammaUserFactory],
    gamma_user_course_points_factory: Type[GammaUserCoursePointsFactory],
    event_factory: Type[EventFactory],
    event_configuration_factory: Type[EventConfigurationFactory],
) -> None:
    current_course_id = 'course-v1:OpenedX+DemoX+DemoCourse'
    another_course_id = 'course-v1:RG+Math+2022'
    gamma_user = gamma_user_factory()
    points_amount = 70
    another_gamma_user_course_points = gamma_user_course_points_factory(
        gamma_user=gamma_user,
        course_id=another_course_id,
        points=points_amount,
    )
    event_configuration = event_configuration_factory(award=16)
    event = event_factory(configuration=event_configuration, username=gamma_user.user_uid, course_id=current_course_id)

    gamma_user.update_user_course_points(event)

    another_gamma_user_course_points.refresh_from_db()

    assert another_gamma_user_course_points.points == points_amount


@pytest.mark.django_db
def test_update_user_course_points_does_not_increment_gamma_user_course_points_record_if_event_is_course_independent(
    gamma_user_factory: Type[GammaUserFactory],
    gamma_user_course_points_factory: Type[GammaUserCoursePointsFactory],
    event_factory: Type[EventFactory],
    event_configuration_factory: Type[EventConfigurationFactory],
) -> None:
    gamma_user = gamma_user_factory()
    points_amount = 70
    gamma_user_course_points = gamma_user_course_points_factory(gamma_user=gamma_user, points=points_amount)
    event_configuration = event_configuration_factory(award=16)
    event = event_factory(configuration=event_configuration, username=gamma_user.user_uid, course_id=None)

    gamma_user.update_user_course_points(event)

    gamma_user_course_points.refresh_from_db()

    assert gamma_user_course_points.points == points_amount


@pytest.mark.django_db
@patch.multiple(
    'users.models.GammaUser',
    update_user_progress=Mock(),
    update_user_chart=Mock(),
    update_user_points=Mock(),
    update_user_course_points=Mock(),
)
@factory.django.mute_signals(signals.post_save)
def test_run_update_user_pipeline_calls_user_data_updates(
    gamma_user_factory: Type[GammaUserFactory],
    event_factory: Type[EventConfigurationFactory],
    event_configuration_factory: Type[EventConfigurationFactory],
) -> None:
    award = 16
    gamma_user = gamma_user_factory()
    event_configuration = event_configuration_factory(award=award)
    event = event_factory(configuration=event_configuration, username=gamma_user.user_uid)

    gamma_user.run_update_user_pipeline(event)

    gamma_user.update_user_progress.assert_called_once_with(award)
    gamma_user.update_user_chart.assert_called_once_with(event_configuration)
    gamma_user.update_user_points.assert_called_once_with(award)
    gamma_user.update_user_course_points.assert_called_once_with(event)
