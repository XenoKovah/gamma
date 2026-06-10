import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.utils.timezone import now

from achievements.models import Achievement, AchievementRule
from avatars.factories import AvatarFactory, AvatarSetFactory
from badges.models import Badge

pytestmark = pytest.mark.django_db

CERT_EVENT = 'edx_certificate_created'


@pytest.fixture
def shared_rule_setup(
    event_configuration_factory,
    rule_factory,
    badge_factory,
    gamma_user_factory,
    achievement_factory,
    achievement_rule_factory,
):
    """
    A user starved by the old selection bug: the shared rule is completed under
    the avatar, while the badge carrying the same rule has no achievement.
    """
    configuration = event_configuration_factory(event_type__name=CERT_EVENT)
    # Empty filters so the replayed event matches the rule (RuleFactory's default
    # filters scope to a fixed course the factory event would not satisfy).
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
    return configuration, rule, badge, user


def badge_achievements(badge, user):
    return Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    )


def test_backfill_creates_and_completes_starved_badge_achievement(shared_rule_setup, event_factory):
    configuration, rule, badge, user = shared_rule_setup
    # The user's historical event of the rule's type (its arrival predates the
    # fix, so it never created the badge achievement).
    event_factory(configuration=configuration, username=user.user_uid)
    badge_achievements(badge, user).delete()

    call_command('backfill_shared_rule_achievements')

    achievement = badge_achievements(badge, user).get()
    assert achievement.all_rules_completed
    assert achievement.completed_at is not None


def test_backfill_dry_run_changes_nothing(shared_rule_setup, event_factory):
    configuration, rule, badge, user = shared_rule_setup
    event_factory(configuration=configuration, username=user.user_uid)
    badge_achievements(badge, user).delete()

    call_command('backfill_shared_rule_achievements', '--dry-run')

    assert not badge_achievements(badge, user).exists()


def test_backfill_skips_users_without_a_matching_event(shared_rule_setup):
    configuration, rule, badge, user = shared_rule_setup

    call_command('backfill_shared_rule_achievements')

    assert not badge_achievements(badge, user).exists()


def test_backfill_respects_rule_id_filter(shared_rule_setup, event_factory):
    configuration, rule, badge, user = shared_rule_setup
    event_factory(configuration=configuration, username=user.user_uid)
    badge_achievements(badge, user).delete()

    call_command('backfill_shared_rule_achievements', '--rule-id', str(rule.id + 1000))

    assert not badge_achievements(badge, user).exists()
