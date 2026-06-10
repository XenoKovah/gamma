import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from achievements.models import Achievement, AchievementRule
from avatars.factories import AvatarFactory, AvatarSetFactory
from badges.models import Badge
from events.enums import RggInternalEventTypes
from events.models import Event

pytestmark = pytest.mark.django_db

CERT_EVENT = 'edx_certificate_created'


def obtained_event_count(user):
    return Event.objects.filter(
        username=user.user_uid,
        configuration__event_type__name=RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value,
    ).count()


def test_badge_sharing_completed_avatar_rule_completes_through_real_pipeline(
    event_configuration_factory,
    rule_factory,
    badge_factory,
    gamma_user_factory,
    achievement_factory,
    achievement_rule_factory,
    event_factory,
):
    """
    End-to-end regression for the shared-rule starvation: with the user's
    avatar instance of the rule already completed, an incoming event must still
    create, evaluate, and complete the badge's instance — and re-processing an
    already-complete achievement must not re-fire the internal obtained event.
    """
    configuration = event_configuration_factory(event_type__name=CERT_EVENT)
    # Explicit empty filters: RuleFactory's default filters scope to a fixed
    # course, which the factory-built event would not match (the rule would be
    # filtered out before the backends, masking the behavior under test).
    rule = rule_factory(event_configuration=configuration, action={CERT_EVENT: {'count': 1}}, filters={})
    badge = badge_factory(set_rules=rule)
    avatar = AvatarFactory(set_rules=rule)
    AvatarSetFactory(is_draft=False, avatars=(avatar,))
    user = gamma_user_factory()

    avatar_achievement = achievement_factory(
        user=user,
        content_type=ContentType.objects.get_for_model(type(avatar)),
        object_id=avatar.id,
        completed_at=now(),
    )
    achievement_rule_factory(
        achievement=avatar_achievement, rule=rule, status=AchievementRule.Statuses.COMPLETED,
    )

    event_factory(configuration=configuration, username=user.user_uid)

    badge_content_type = ContentType.objects.get_for_model(Badge)
    badge_achievement = Achievement.objects.get(
        user=user, content_type=badge_content_type, object_id=badge.id,
    )
    assert badge_achievement.all_rules_completed
    assert badge_achievement.completed_at is not None
    assert badge_achievement.notification_seen_at is None
    # Exactly one "achievement obtained" internal event: the badge's first
    # completion. The avatar's pre-completed instance must not re-fire.
    assert obtained_event_count(user) == 1

    # A second matching event finds every carrier complete: the rule is no
    # longer selected, nothing is re-fired, no duplicate achievements appear.
    event_factory(configuration=configuration, username=user.user_uid)

    assert Achievement.objects.filter(
        user=user, content_type=badge_content_type, object_id=badge.id,
    ).count() == 1
    assert obtained_event_count(user) == 1
