import pytest
from django.contrib.contenttypes.models import ContentType

from achievements.models import AchievementRule
from avatars.models import Avatar


@pytest.fixture
def completed_achievement_for_avatar(achievement_factory, achievement_rule_factory):
    """
    Create a completed achievement for an avatar.
    """

    def _create(user, avatar):
        content_type = ContentType.objects.get_for_model(Avatar)

        achievement = achievement_factory(
            user=user,
            content_type=content_type,
            object_id=avatar.id,
            title=avatar.title,
        )

        for rule in avatar.rules.all():
            achievement_rule_factory(
                achievement=achievement,
                rule=rule,
                status=AchievementRule.Statuses.COMPLETED,
            )

        return achievement

    return _create


@pytest.fixture
def active_achievement_for_avatar(achievement_factory, achievement_rule_factory):
    """
    Create an active (in-progress) achievement for an avatar.
    """

    def _create(user, avatar):
        content_type = ContentType.objects.get_for_model(Avatar)

        achievement = achievement_factory(
            user=user,
            content_type=content_type,
            object_id=avatar.id,
            title=avatar.title,
        )

        for rule in avatar.rules.all():
            achievement_rule_factory(
                achievement=achievement,
                rule=rule,
                status=AchievementRule.Statuses.ACTIVE,
            )

        return achievement

    return _create


@pytest.fixture
def user_with_completed_avatar_stages(
    user_avatar_config_with_stages,
    completed_achievement_for_avatar,
):
    """
    Create a user with completed avatar stages.
    """

    def _create(user_points=100, stages=3, points_per_stage=50, completed_stages=1):
        config = user_avatar_config_with_stages(
            user_points=user_points,
            stages=stages,
            points_per_stage=points_per_stage,
        )
        user = config.user
        avatar_set = config.avatar_set

        avatars = list(avatar_set.avatars.order_by("stage")[:completed_stages])
        for avatar in avatars:
            completed_achievement_for_avatar(user=user, avatar=avatar)

        return config

    return _create
