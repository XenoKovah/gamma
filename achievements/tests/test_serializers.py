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

        # Title/description come from the current badge, not the award-time snapshot.
        assert data['title'] == badge.title
        assert data['description'] == badge.description
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

        assert data['title'] == badge.title
        assert data['description'] == badge.description
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

        assert data['title'] == badge.title
        assert data['description'] == badge.description
        assert data['done'] is False
        assert data['progress'] == achievement.achievement_dependencies
        assert data['object_id'] == achievement.object_id
        assert data['object_uri'] == achievement.content_object.image.url
        assert data['slug'] == badge.slug
        assert data['is_active'] == badge.is_active

    def test_title_and_description_follow_badge_rename(self, achievement_factory, badge_factory):
        """A badge rename is reflected immediately, not frozen at award time."""
        content_type = ContentType.objects.get_for_model(Badge)
        badge = badge_factory(title='Received a Post Like', description='Original description.')
        achievement = achievement_factory(
            content_type=content_type,
            content_object=badge,
            title='⑧ Received a Post Like',  # stale award-time snapshot
            description='Stale snapshot description.',
        )

        badge.title = 'Received a Post Like'
        badge.description = 'Updated description.'
        badge.save()

        data = AchievementDetailSerializer(achievement).data

        assert data['title'] == 'Received a Post Like'
        assert data['description'] == 'Updated description.'

    def test_falls_back_to_snapshot_when_badge_title_blank(self, achievement_factory, badge_factory):
        """When the badge has no title/description, the achievement snapshot is used."""
        content_type = ContentType.objects.get_for_model(Badge)
        badge = badge_factory(title='', description='')
        achievement = achievement_factory(
            content_type=content_type,
            content_object=badge,
            title='Snapshot title',
            description='Snapshot description',
        )

        data = AchievementDetailSerializer(achievement).data

        assert data['title'] == 'Snapshot title'
        assert data['description'] == 'Snapshot description'

    def test_serializer_with_broken_rules_and_object(self, achievement_factory):
        content_type = ContentType.objects.get_for_model(Badge)
        achievement = achievement_factory(content_type=content_type)

        serializer = AchievementDetailSerializer(achievement)
        data = serializer.data

        # No resolvable badge -> fall back to the achievement's own snapshot.
        assert data['title'] == achievement.title
        assert data['description'] == achievement.description
        assert data['done'] is True
        assert data['progress'] is None
        assert data['object_id'] == achievement.object_id
        assert data['object_uri'] is None
        assert data['slug'] is None
        assert data['is_active'] is None

    def test_serializer_exposes_badge_completion_points(self, achievement_factory, badge_factory):
        content_type = ContentType.objects.get_for_model(Badge)
        badge = badge_factory(points=10000)
        achievement = achievement_factory(content_type=content_type, content_object=badge)

        data = AchievementDetailSerializer(achievement).data

        assert data['points'] == 10000
