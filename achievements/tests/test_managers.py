import pytest
from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement, AchievementRule

pytestmark = pytest.mark.django_db


class TestCreateAchievementBasedOnEvent:
    """
    Test suite for validating the creation of achievements and achievement rules.

    This test suite ensures that achievements are correctly created based on the provided
    user, event, and backend instance. It also verifies that associated rules and dependencies
    are properly set.
    """

    def test_create_achievement_check_basic_fields_with_status(
        self,
        rule_factory,
        event_factory,
        badge_factory,
        gamma_user_factory,
        mock_action_event_based_dict,
    ):
        """
        Test that achievement is correctly created with the expected basic fields.

        Ensures:
        - The achievement is successfully created.
        - The title and description match the associated badge.
        - The content type and object ID are correctly assigned.
        """
        user = gamma_user_factory()
        event = event_factory()
        rule = rule_factory(event_configuration=event.configuration, action=mock_action_event_based_dict)
        badge = badge_factory(set_rules=(rule,))

        Achievement.objects.create_achievement(user=user, event=event, instance=badge)

        achievement = Achievement.objects.last()

        assert achievement is not None
        assert achievement.title == badge.title
        assert achievement.description == badge.description

        content_type = ContentType.objects.get_for_model(type(badge))
        assert achievement.content_type == content_type
        assert achievement.object_id == badge.id

    def test_create_achievement_check_rule(
        self,
        rule_factory,
        event_factory,
        badge_factory,
        gamma_user_factory,
    ):
        """
        Test that achievement rule is correctly associated with the created achievement.

        Ensures:
        - An achievement is created.
        - The correct number of achievement rules are associated.
        - The rule's status is set to ACTIVE(default status).
        """
        user = gamma_user_factory()
        event = event_factory()
        rule = rule_factory(event_configuration=event.configuration, action={event.configuration.event_name: 3})
        badge = badge_factory(set_rules=(rule,))

        Achievement.objects.create_achievement(user=user, event=event, instance=badge)

        achievement = Achievement.objects.last()
        achievement_rules = achievement.achievement_rules.filter(achievement=achievement)

        assert achievement_rules.count() == 1

        achievement_rule = achievement_rules.first()
        assert achievement_rule.rule == badge.rules.first()
        assert achievement_rule.status == AchievementRule.Statuses.ACTIVE

    def test_create_achievement_rule_check_dependencies(
        self,
        rule_factory,
        event_factory,
        badge_factory,
        gamma_user_factory,
    ):
        """
        Test that the achievement rule correctly registers dependencies.

        Ensures:
        - The rule contains an 'events' dependency.
        - The correct event key name is stored in the dependencies.
        """
        user = gamma_user_factory()
        event = event_factory()
        rule = rule_factory(event_configuration=event.configuration, action={event.configuration.event_name: 3})
        badge = badge_factory(set_rules=(rule,))

        Achievement.objects.create_achievement(user=user, event=event, instance=badge)

        achievement = Achievement.objects.last()
        achievement_rule = achievement.achievement_rules.first()

        assert 'events' in achievement_rule.dependencies
        assert event.configuration.event_name in achievement_rule.dependencies['events']

    def test_create_achievement_rule_check_event_action(
        self,
        rule_factory,
        event_factory,
        badge_factory,
        gamma_user_factory,
    ):
        """
        Test that the achievement rule correctly records event actions.

        Ensures:
        - The event action includes a 'goal' field matching the rule action.
        - The 'count' field initializes at 1 by default.
        - The 'last' field exists in the event action.
        """
        user = gamma_user_factory()
        event = event_factory()
        event_name_mock = event.configuration.event_name
        event_count_mock = 3
        rule = rule_factory(event_configuration=event.configuration, action={event_name_mock: event_count_mock})
        badge = badge_factory(set_rules=(rule,))

        Achievement.objects.create_achievement(user=user, event=event, instance=badge)

        achievement = Achievement.objects.last()
        achievement_rule = achievement.achievement_rules.first()

        event_json = achievement_rule.dependencies['events'][event_name_mock]
        assert 'goal' in event_json
        assert event_json['goal'] == event_count_mock
        assert 'count' in event_json
        assert event_json['count'] == 1
        assert 'last' in event_json


class TestUpdateAchievementBasedOnEvent:
    """
    Test suite for validating the update functionality of achievements and achievement rules.

    These tests ensure that existing achievements are correctly updated based on new event
    occurrences, updating rule dependencies and statuses.
    """

    def test_update_achievement_basic_fields_with_status(self, achievement_with_events_dependencies):
        """
        Test that achievement is updated correctly.

        Ensures:
        - The achievement is updated with new event.
        - The rule associated with the achievement is marked as COMPLETED if the goal is met.
        - The achievement's content type and object ID remain unchanged.
        """
        user, event, badge, achievement, _ = achievement_with_events_dependencies(event_count_mock=2)

        Achievement.objects.update_achievement(user=user, event=event, instance=badge)
        achievement.refresh_from_db()
        achievement_rule = achievement.achievement_rules.first()

        assert achievement_rule.rule == badge.rules.first()
        assert achievement_rule.status == AchievementRule.Statuses.COMPLETED

        content_type = ContentType.objects.get_for_model(type(badge))
        assert achievement.content_type == content_type
        assert achievement.object_id == badge.id

    def test_update_achievement_rule(self, achievement_with_events_dependencies):
        """
        Test that achievement rule is correctly updated with own dependencies.

        Ensures:
        - The achievement rule remains ACTIVE if the goal is not yet met.
        - The correct number of achievement rules are associated with the updated achievement.
        - The rule dependencies are correctly updated with new event data.
        """
        user, event, badge, achievement, event_name_mock = achievement_with_events_dependencies(
            event_count_mock=3, initial_count=1, goal=3
        )

        Achievement.objects.update_achievement(user=user, event=event, instance=badge)

        achievement = Achievement.objects.last()
        achievement_rules = achievement.achievement_rules.filter(achievement=achievement)

        assert achievement_rules.count() == 1
        achievement_rule = achievement_rules.first()

        assert achievement_rule.rule == badge.rules.first()
        assert achievement_rule.status == AchievementRule.Statuses.ACTIVE
        assert 'events' in achievement_rule.dependencies
        assert event_name_mock in achievement_rule.dependencies['events']

    def test_update_achievement_rule_event_action(self, achievement_with_events_dependencies):
        """
        Test that the achievement rule correctly updates its event action counts.

        Ensures:
        - The event action contains the correct 'goal' value.
        - The 'count' field increments appropriately.
        - The 'last' field is correctly updated.
        """
        user, event, badge, achievement, event_name_mock = achievement_with_events_dependencies(
            event_count_mock=3, initial_count=1, goal=3
        )

        Achievement.objects.update_achievement(user=user, event=event, instance=badge)

        achievement = Achievement.objects.last()
        achievement_rule = achievement.achievement_rules.first()

        event_json = achievement_rule.dependencies['events'][event_name_mock]
        assert 'goal' in event_json
        assert event_json['goal'] == 3
        assert 'count' in event_json
        assert event_json['count'] == 2
        assert 'last' in event_json
