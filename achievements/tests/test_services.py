from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from badges.models import Badge

from .constants import mock_event_based_name, mock_achievement_based_name

pytestmark = pytest.mark.django_db


class TestRuleDependencyServiceEventBased:
    """
    Test suite for RuleDependencyService focusing on event-based dependencies.
    """

    def test_create_or_update_with_valid_event(self, rule_dependency_service, mock_action_event_based_dict):
        """
        Test that `create_or_update` correctly updates dependencies for valid events.
        """
        service = rule_dependency_service()
        updated_dependencies = service.create_or_update(actions=mock_action_event_based_dict)

        assert 'events' in updated_dependencies
        event_data = updated_dependencies['events'][mock_event_based_name]

        assert event_data == {
            'count': 1,
            'goal': 3,
            'last': service.event_created_at.isoformat()
        }

    @pytest.mark.parametrize('invalid_actions', [
        {123: 'not an event'},
        {mock_event_based_name: 'wrong type'},
        {mock_event_based_name: None},
    ], ids=[
        'Failed: Invalid key type',
        'Failed: Invalid value type',
        'Failed: None as a value',
    ])
    def test_create_or_update_skips_invalid_actions(self, rule_dependency_service, invalid_actions):
        """
        Test that `create_or_update` ignores invalid actions without modifying dependencies.
        """
        service = rule_dependency_service()

        dependencies_before = service.dependencies.copy()
        updated_dependencies = service.create_or_update(actions=invalid_actions)

        assert updated_dependencies == dependencies_before

    @pytest.mark.parametrize('initial_count,expected_count', [
        (1, 2),
        (2, 3),
    ], ids=[
        'Passed: Second occurrence',
        'Passed: Multiple increments',
    ])
    def test_event_handler_increments_event_count(
        self,
        rule_dependency_service,
        mock_action_event_based_dict,
        initial_count,
        expected_count
    ):
        """
        Test that `_handle_event` increments event count correctly.
        """
        initial_dependencies = {
            'events': {
                mock_event_based_name: {
                    'count': initial_count,
                    'goal': 3,  # taken from value of mock_action_event_based_dict
                    'last': now().isoformat()
                }
            }
        }

        service = rule_dependency_service(dependencies=initial_dependencies)
        updated_dependencies = service.create_or_update(actions=mock_action_event_based_dict)

        event_data = updated_dependencies['events'][mock_event_based_name]

        assert event_data == {
            'count': expected_count,
            'goal': 3,
            'last': service.event_created_at.isoformat()
        }

    @pytest.mark.parametrize('last_event_days_ago,expected_count', [
        (1, 3),
        (2, 3),
        (3, 1),
    ], ids=[
        'Passed: Within frequency, 1 day, should increment',
        'Passed: Within frequency, 2 day, should increment',
        'Passed: Exceeds frequency, should reset',
    ])
    def test_event_handler_resets_count_based_on_frequency(
        self,
        rule_dependency_service,
        mock_action_event_based_dict,
        last_event_days_ago,
        expected_count
    ):
        """
        Test that `_handle_event` resets event count when frequency threshold (3) is exceeded.
        """
        past_event_time = now() - timedelta(days=last_event_days_ago)
        initial_dependencies = {
            'events': {
                mock_event_based_name: {
                    'count': 2,
                    'goal': 3,  # taken from value of mock_action_event_based_dict
                    'last': past_event_time.isoformat()
                }
            }
        }

        service = rule_dependency_service(dependencies=initial_dependencies)
        updated_dependencies = service.create_or_update(actions=mock_action_event_based_dict)

        event_data = updated_dependencies['events'][mock_event_based_name]

        assert event_data == {
            'count': expected_count,
            'goal': 3,
            'last': service.event_created_at.isoformat()
        }


class TestRuleDependencyServiceAchievementBased:
    """
    Test suite for RuleDependencyService focusing on dependent achievement-based dependencies.
    """

    def test_create_or_update_with_valid_event(
        self,
        event_configuration_factory,
        rule_factory,
        rule_dependency_service,
        mock_action_achievement_based_dict,
        mock_dependent_badge,
    ):
        """
        Test that `create_or_update` correctly updates dependencies for valid event.
        """
        badge_content_type = ContentType.objects.get_for_model(Badge)

        event_configuration = event_configuration_factory(
            event_type__name=mock_achievement_based_name,
            is_depends_on_achievement=True,
            content_type=badge_content_type,
        )
        rule = rule_factory(
            event_configuration=event_configuration,
            action=mock_action_achievement_based_dict,
        )
        service = rule_dependency_service(rule=rule)
        updated_dependencies = service.create_or_update(actions=mock_action_achievement_based_dict)

        assert 'achievements' in updated_dependencies

        expected_achievement = {
            'content_type_id': badge_content_type.id,
            'content_type': badge_content_type.name,
            'id': mock_dependent_badge.id,
        }
        assert expected_achievement in service.dependencies['achievements']
