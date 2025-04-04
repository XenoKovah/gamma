import pytest

from django.contrib.contenttypes.models import ContentType

from achievements.models import AchievementRule
from achievements.serializers import AchievementDetailSerializer
from badges.models import Badge


@pytest.mark.django_db
class TestAchievementDetailSerializer:
    """
    Test Case for the testing AchievementDetailSerializer.
    """

    def test_serializer_with_completed_achievement(self, achievement_factory, achievement_rule_factory, badge_factory):
        content_type = ContentType.objects.get_for_model(Badge)
        badge = badge_factory()
        achievement = achievement_factory(content_type=content_type, content_object=badge)
        achievement_rule_factory(achievement=achievement, status=AchievementRule.Statuses.COMPLETED)

        serializer = AchievementDetailSerializer(achievement)
        data = serializer.data

        assert data['title'] == achievement.title
        assert data['description'] == achievement.description
        assert data['done'] is True
        assert data['progress'] == achievement.achievement_dependencies
        assert data['object_id'] == achievement.object_id
        assert data['object_uri'] == achievement.content_object.image.url
        assert data['slug'] == badge.slug
        assert data['is_active'] == badge.is_active

    def test_serializer_with_active_achievement(self, achievement_factory, achievement_rule_factory, badge_factory):
        content_type = ContentType.objects.get_for_model(Badge)
        badge = badge_factory()
        achievement = achievement_factory(content_type=content_type, content_object=badge)
        achievement_rule_factory(achievement=achievement, status=AchievementRule.Statuses.ACTIVE)

        serializer = AchievementDetailSerializer(achievement)
        data = serializer.data

        assert data['title'] == achievement.title
        assert data['description'] == achievement.description
        assert data['done'] is False
        assert data['progress'] == achievement.achievement_dependencies
        assert data['object_id'] == achievement.object_id
        assert data['object_uri'] == achievement.content_object.image.url
        assert data['slug'] == badge.slug
        assert data['is_active'] == badge.is_active

    def test_serializer_with_failed_achievement(self, achievement_factory, achievement_rule_factory, badge_factory):
        content_type = ContentType.objects.get_for_model(Badge)
        badge = badge_factory()
        achievement = achievement_factory(content_type=content_type, content_object=badge)
        achievement_rule_factory(achievement=achievement, status=AchievementRule.Statuses.FAILED)

        serializer = AchievementDetailSerializer(achievement)
        data = serializer.data

        assert data['title'] == achievement.title
        assert data['description'] == achievement.description
        assert data['done'] is False
        assert data['progress'] == achievement.achievement_dependencies
        assert data['object_id'] == achievement.object_id
        assert data['object_uri'] == achievement.content_object.image.url
        assert data['slug'] == badge.slug
        assert data['is_active'] == badge.is_active

    def test_serializer_with_broken_rules_and_object(self, achievement_factory):
        content_type = ContentType.objects.get_for_model(Badge)
        achievement = achievement_factory(content_type=content_type)

        serializer = AchievementDetailSerializer(achievement)
        data = serializer.data

        assert data['title'] == achievement.title
        assert data['description'] == achievement.description
        assert data['done'] is True
        assert data['progress'] is None
        assert data['object_id'] == achievement.object_id
        assert data['object_uri'] is None
        assert data['slug'] is None
        assert data['is_active'] is None
