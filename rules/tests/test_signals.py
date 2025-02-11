import pytest

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

    event = event_factory(configuration=rule.event_configuration, username=user.user_uid)

    mock_gamification_backends.process_achievement.assert_called_once_with(rule, event, user, False)


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
