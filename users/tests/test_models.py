import pytest
from datetime import datetime

from events.factories import EventFactory
from users.factories import GammaUserFactory


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
    formatted_date = date.strftime('%Y.%m.%d')
    points_key = f'progress.{year}.points'
    points_by_day_key = f'progress.{year}'

    assert gamma_user.progress[points_key] == event_points
    assert gamma_user.progress[points_by_day_key][formatted_date] == event_points


@pytest.mark.django_db
def test_update_user_chart(gamma_user_factory: GammaUserFactory, event_configuration_factory: EventFactory) -> None:
    """
    Test the `update_user_chart` class method.
    """
    gamma_user = gamma_user_factory()
    configuration = event_configuration_factory()

    gamma_user.update_user_chart(configuration)

    gamma_user.refresh_from_db()

    event_chart_key = f'chart.{configuration.event_type.name}'

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
