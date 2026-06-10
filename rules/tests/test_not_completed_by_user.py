import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from achievements.models import AchievementRule
from avatars.factories import AvatarFactory, AvatarSetFactory
from avatars.models import Avatar
from badges.models import Badge
from rules.models import Rule

pytestmark = pytest.mark.django_db


@pytest.fixture
def configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name='edx_certificate_created')


@pytest.fixture
def rule(rule_factory, configuration):
    return rule_factory(
        event_configuration=configuration,
        action={'edx_certificate_created': {'count': 1}},
    )


def make_instance(achievement_factory, achievement_rule_factory, user, content_object, rule, status):
    """
    Build the user's achievement instance of ``rule`` under ``content_object``.
    """
    achievement = achievement_factory(
        user=user,
        content_type=ContentType.objects.get_for_model(type(content_object)),
        object_id=content_object.id,
        completed_at=now() if status == AchievementRule.Statuses.COMPLETED else None,
    )
    achievement_rule_factory(achievement=achievement, rule=rule, status=status)
    return achievement


def selected(configuration, user):
    return list(Rule.objects.not_completed_by_user(configuration, user))


def test_fresh_user_with_badge_carrier_is_selected(rule, configuration, badge_factory, gamma_user_factory):
    badge_factory(set_rules=rule)

    assert selected(configuration, gamma_user_factory()) == [rule]


def test_rule_completed_under_avatar_stays_selected_for_pending_badge(
    rule, configuration, badge_factory, gamma_user_factory, achievement_factory, achievement_rule_factory
):
    """
    The starvation bug: completing the shared rule under the avatar must NOT
    stop the badge carrying the same rule from being processed.
    """
    user = gamma_user_factory()
    badge_factory(set_rules=rule)
    avatar = AvatarFactory(set_rules=rule)
    AvatarSetFactory(is_draft=False, avatars=(avatar,))
    make_instance(
        achievement_factory, achievement_rule_factory, user, avatar, rule, AchievementRule.Statuses.COMPLETED,
    )

    assert selected(configuration, user) == [rule]


def test_rule_completed_under_every_carrier_is_excluded(
    rule, configuration, badge_factory, gamma_user_factory, achievement_factory, achievement_rule_factory
):
    user = gamma_user_factory()
    badge = badge_factory(set_rules=rule)
    avatar = AvatarFactory(set_rules=rule)
    AvatarSetFactory(is_draft=False, avatars=(avatar,))
    make_instance(achievement_factory, achievement_rule_factory, user, avatar, rule, AchievementRule.Statuses.COMPLETED)
    make_instance(achievement_factory, achievement_rule_factory, user, badge, rule, AchievementRule.Statuses.COMPLETED)

    assert selected(configuration, user) == []


def test_active_instance_keeps_rule_selected(
    rule, configuration, badge_factory, gamma_user_factory, achievement_factory, achievement_rule_factory
):
    user = gamma_user_factory()
    badge = badge_factory(set_rules=rule)
    make_instance(achievement_factory, achievement_rule_factory, user, badge, rule, AchievementRule.Statuses.ACTIVE)

    assert selected(configuration, user) == [rule]


def test_completed_sole_badge_excludes_rule(
    rule, configuration, badge_factory, gamma_user_factory, achievement_factory, achievement_rule_factory
):
    user = gamma_user_factory()
    badge = badge_factory(set_rules=rule)
    make_instance(achievement_factory, achievement_rule_factory, user, badge, rule, AchievementRule.Statuses.COMPLETED)

    assert selected(configuration, user) == []


def test_rule_without_carriers_is_excluded(rule, configuration, gamma_user_factory):
    assert selected(configuration, gamma_user_factory()) == []


def test_inactive_badge_does_not_keep_rule_selected(rule, configuration, badge_factory, gamma_user_factory):
    badge_factory(set_rules=rule, is_active=False)

    assert selected(configuration, gamma_user_factory()) == []


def test_draft_set_avatar_does_not_keep_rule_selected(rule, configuration, gamma_user_factory):
    avatar = AvatarFactory(set_rules=rule)
    AvatarSetFactory(is_draft=True, avatars=(avatar,))

    assert selected(configuration, gamma_user_factory()) == []


def test_per_user_isolation(
    rule, configuration, badge_factory, gamma_user_factory, achievement_factory, achievement_rule_factory
):
    """
    One user's completion must not affect another user's selection.
    """
    badge = badge_factory(set_rules=rule)
    finisher, newcomer = gamma_user_factory(), gamma_user_factory()
    make_instance(
        achievement_factory, achievement_rule_factory, finisher, badge, rule, AchievementRule.Statuses.COMPLETED,
    )

    assert selected(configuration, finisher) == []
    assert selected(configuration, newcomer) == [rule]
