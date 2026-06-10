from typing import Type
from unittest.mock import MagicMock, Mock, patch

import pytest

from events.enums import RggInternalEventTypes
from events.models import Event
from events.factories import EventFactory
from users.factories import GammaUserFactory

pytestmark = pytest.mark.django_db


@pytest.mark.enable_signals
def test_process_event_creation_with_backends(
    rule_factory,
    event_factory,
    badge_factory,
    mock_rules_filter,
    gamma_user_factory,
    mock_gamification_backends,
):
    user = gamma_user_factory()
    badge = badge_factory()
    rule = rule_factory()
    badge.rules.add(rule)

    mock_rules_filter.filter_rules.return_value = [rule]

    edx_event = event_factory(configuration=rule.event_configuration, username=user.user_uid)
    rgg_internal_event = Event.objects.filter(
        username=user.user_uid, configuration__event_type__name=RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value
    ).first()

    mock_gamification_backends.process_achievement.call_args_list[0].assert_called_once_with(rule, edx_event, user)
    mock_gamification_backends.process_achievement.call_args_list[1].assert_called_once_with(
        rule, rgg_internal_event, user
    )


@pytest.mark.enable_signals
def test_process_event_creation_with_no_relevant_rules(
    event_factory,
    mock_rules_filter,
    gamma_user_factory,
    mock_gamification_backends,
):
    user = gamma_user_factory()
    mock_rules_filter.filter_rules.return_value = []

    event_factory(username=user.username)

    mock_gamification_backends.process_achievement.assert_not_called()


@patch('rules.signals.RulesFilterService', MagicMock())
@patch('rules.signals.Rule', Mock())
@patch('rules.signals.GammaUser')
def test_process_event_creation_runs_update_user_pipeline(
    gamma_user_mock: MagicMock,
    gamma_user_factory: Type[GammaUserFactory],
    event_factory: Type[EventFactory],
) -> None:
    user_uid = 'test_user'
    gamma_user_factory(user_uid=user_uid)

    event = event_factory(username=user_uid)

    gamma_user_mock.ensure_gamma_user_is_created.assert_called_once_with(user_uid=user_uid)
    # The user is re-fetched under a row lock before processing, so the pipeline
    # runs on the locked instance rather than the ensure_* return value.
    locked_user = gamma_user_mock.objects.select_for_update.return_value.get.return_value
    locked_user.run_update_user_pipeline.assert_called_once_with(event)
