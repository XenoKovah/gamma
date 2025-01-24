import pytest

from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement, AchievementRule


pytestmark = pytest.mark.django_db


def test_create_draft_achievement(
    rule_factory,
    event_factory,
    badge_factory,
    gamma_user_factory,
):
    user = gamma_user_factory()
    event = event_factory()
    rule = rule_factory(event_configuration=event.configuration)
    badge = badge_factory(set_rules=(rule,))

    assert Achievement.objects.count() == 0
    assert AchievementRule.objects.count() == 0

    Achievement.objects.create_draft_achievement(user=user, event=event, instance=badge)

    achievement = Achievement.objects.last()

    assert achievement is not None
    assert achievement.title == badge.title
    assert achievement.description == badge.description

    content_type = ContentType.objects.get_for_model(type(badge))
    assert achievement.content_type == content_type
    assert achievement.object_id == badge.id

    achievement_rules = achievement.achievement_rules.filter(achievement=achievement)
    assert achievement_rules.count() == 1

    achievement_rule = achievement_rules.first()
    assert achievement_rule.rule == badge.rules.first()
    assert achievement_rule.status == AchievementRule.Statuses.ACTIVE
