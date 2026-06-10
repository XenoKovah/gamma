import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from achievements.models import Achievement, AchievementRule
from achievements.reconciliation import recompute_holders
from badges.models import Badge
from events.models import Event
from rules.signals import process_event_creation

pytestmark = pytest.mark.django_db

CERT_EVENT = 'edx_certificate_created'
COURSE_A = 'course-v1:org+A+1'
COURSE_B = 'course-v1:org+B+1'
COURSE_C = 'course-v1:org+C+1'
COMPLETED = AchievementRule.Statuses.COMPLETED


@pytest.fixture(autouse=True)
def isolate_from_event_pipeline():
    """
    Recompute must be the only actor here, so raw Event creation should not drive the live pipeline.
    """
    was_connected = post_save.disconnect(process_event_creation, sender=Event)
    yield
    if was_connected:
        post_save.connect(process_event_creation, sender=Event)


@pytest.fixture
def cert_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name=CERT_EVENT)


@pytest.fixture
def badge_content_type():
    return ContentType.objects.get_for_model(Badge)


def _cert_rule(rule_factory, configuration, course):
    return rule_factory(
        event_configuration=configuration,
        action={CERT_EVENT: {'count': 1}},
        filters={'course': course},
    )


def _earn_cert(event_factory, configuration, user, course):
    return event_factory(configuration=configuration, username=user.user_uid, course_id=course)


def test_recompute_grants_users_who_already_completed_the_courses(
    cert_configuration, badge_factory, rule_factory, event_factory, gamma_user_factory,
):
    """
    A user who certified in every required course before the badge existed should be granted it.
    """
    user = gamma_user_factory()
    _earn_cert(event_factory, cert_configuration, user, COURSE_A)
    _earn_cert(event_factory, cert_configuration, user, COURSE_B)

    badge = badge_factory()
    badge.rules.set([
        _cert_rule(rule_factory, cert_configuration, COURSE_A),
        _cert_rule(rule_factory, cert_configuration, COURSE_B),
    ])

    assert not Achievement.objects.filter(object_id=badge.id, user=user).exists()

    result = recompute_holders(badge)

    assert user.user_uid in result.granted
    achievement = Achievement.objects.get(object_id=badge.id, user=user)
    assert achievement.all_rules_completed


def test_recompute_is_noop_for_rule_less_manual_badge(
    badge_content_type, badge_factory, achievement_factory, gamma_user_factory,
):
    """
    A badge with no rules is assigned manually; recompute must leave its holders untouched
    rather than treating the rule-less grant as "no longer qualifies" and revoking it.
    """
    user = gamma_user_factory()
    badge = badge_factory()  # no rules
    assert not badge.rules.exists()

    # Manually granted: a rule-less Achievement, which reads as completed/earned.
    achievement = achievement_factory(user=user, content_type=badge_content_type, object_id=badge.id)
    assert achievement.all_rules_completed

    result = recompute_holders(badge)

    assert result.granted == []
    assert result.revoked == []
    assert Achievement.objects.filter(object_id=badge.id, user=user).exists()


def test_recompute_revokes_holder_when_a_course_is_added(
    cert_configuration, badge_content_type, badge_factory, rule_factory, event_factory,
    achievement_factory, achievement_rule_factory, gamma_user_factory,
):
    """
    Adding course C to a live A&B badge must revoke holders who lack C.
    """
    user = gamma_user_factory()
    rule_a = _cert_rule(rule_factory, cert_configuration, COURSE_A)
    rule_b = _cert_rule(rule_factory, cert_configuration, COURSE_B)
    rule_c = _cert_rule(rule_factory, cert_configuration, COURSE_C)

    badge = badge_factory()
    badge.rules.set([rule_a, rule_b, rule_c])  # now requires A & B & C

    _earn_cert(event_factory, cert_configuration, user, COURSE_A)
    _earn_cert(event_factory, cert_configuration, user, COURSE_B)

    # Prior state: they held the badge under the old {A, B} rules.
    achievement = achievement_factory(user=user, content_type=badge_content_type, object_id=badge.id)
    achievement_rule_factory(achievement=achievement, rule=rule_a, status=COMPLETED)
    achievement_rule_factory(achievement=achievement, rule=rule_b, status=COMPLETED)
    assert achievement.all_rules_completed

    result = recompute_holders(badge)

    assert user.user_uid in result.revoked
    achievement.refresh_from_db()
    assert not achievement.all_rules_completed


def test_recompute_keeps_users_who_still_qualify(
    cert_configuration, badge_content_type, badge_factory, rule_factory, event_factory,
    achievement_factory, achievement_rule_factory, gamma_user_factory,
):
    """
    A holder who satisfies every current rule is left untouched (no duplicate grant).
    """
    user = gamma_user_factory()
    rule_a = _cert_rule(rule_factory, cert_configuration, COURSE_A)
    rule_b = _cert_rule(rule_factory, cert_configuration, COURSE_B)
    badge = badge_factory()
    badge.rules.set([rule_a, rule_b])

    _earn_cert(event_factory, cert_configuration, user, COURSE_A)
    _earn_cert(event_factory, cert_configuration, user, COURSE_B)

    achievement = achievement_factory(user=user, content_type=badge_content_type, object_id=badge.id)
    achievement_rule_factory(achievement=achievement, rule=rule_a, status=COMPLETED)
    achievement_rule_factory(achievement=achievement, rule=rule_b, status=COMPLETED)

    result = recompute_holders(badge)

    assert user.user_uid not in result.granted
    assert user.user_uid not in result.revoked
    achievement.refresh_from_db()
    assert achievement.all_rules_completed


def test_recompute_does_not_grant_partial_progress(
    cert_configuration, badge_factory, rule_factory, event_factory, gamma_user_factory,
):
    """
    A user who certified in only one of two required courses is left in-progress, not granted.
    """
    user = gamma_user_factory()
    badge = badge_factory()
    badge.rules.set([
        _cert_rule(rule_factory, cert_configuration, COURSE_A),
        _cert_rule(rule_factory, cert_configuration, COURSE_B),
    ])

    _earn_cert(event_factory, cert_configuration, user, COURSE_A)  # only A

    result = recompute_holders(badge)

    assert user.user_uid not in result.granted
    achievement = Achievement.objects.filter(object_id=badge.id, user=user).first()
    assert achievement is not None
    assert not achievement.all_rules_completed
    # Every rule records canonical 'events' progress (goal/count) so the leaderboard percent
    # calc counts it — otherwise a 1-of-2 in-progress badge would render as 100%.
    for achievement_rule in achievement.achievement_rules.all():
        assert 'events' in (achievement_rule.dependencies or {})


def test_recompute_with_or_group_course_filter(
    cert_configuration, badge_factory, rule_factory, event_factory, gamma_user_factory,
):
    """
    A list course filter is an OR group: `A AND (B OR C)` grants to A + (B or C), not to A alone.
    """
    rule_a = _cert_rule(rule_factory, cert_configuration, COURSE_A)
    rule_b_or_c = rule_factory(
        event_configuration=cert_configuration,
        action={CERT_EVENT: {"count": 1}},
        filters={"course": [COURSE_B, COURSE_C]},
    )
    badge = badge_factory()
    badge.rules.set([rule_a, rule_b_or_c])

    user_a_b = gamma_user_factory()           # A + B  -> granted (B satisfies the OR group)
    _earn_cert(event_factory, cert_configuration, user_a_b, COURSE_A)
    _earn_cert(event_factory, cert_configuration, user_a_b, COURSE_B)
    user_a_c = gamma_user_factory()           # A + C  -> granted (C satisfies the OR group)
    _earn_cert(event_factory, cert_configuration, user_a_c, COURSE_A)
    _earn_cert(event_factory, cert_configuration, user_a_c, COURSE_C)
    user_a_only = gamma_user_factory()        # A only -> not granted (OR group unmet)
    _earn_cert(event_factory, cert_configuration, user_a_only, COURSE_A)
    user_b_c = gamma_user_factory()           # B + C but not A -> not granted (AND part unmet)
    _earn_cert(event_factory, cert_configuration, user_b_c, COURSE_B)
    _earn_cert(event_factory, cert_configuration, user_b_c, COURSE_C)

    result = recompute_holders(badge)

    assert user_a_b.user_uid in result.granted
    assert user_a_c.user_uid in result.granted
    assert user_a_only.user_uid not in result.granted
    assert user_b_c.user_uid not in result.granted


DONE_EVENT = 'edx_done_toggled'
DONE_BLOCKS = [f'block-v1:org+A+1+type@done+block@{suffix}' for suffix in 'abcde']


@pytest.fixture
def done_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name=DONE_EVENT)


def _block_set_rule(rule_factory, configuration, blocks):
    return rule_factory(
        event_configuration=configuration,
        action={DONE_EVENT: {'count': len(blocks)}},
        filters={'course': COURSE_A, 'blocks': blocks},
    )


def _mark_done(event_factory, configuration, user, block_id):
    return event_factory(
        configuration=configuration,
        username=user.user_uid,
        course_id=COURSE_A,
        block_id=block_id,
    )


def test_recompute_grants_block_set_badge_from_event_history(
    done_configuration, badge_factory, rule_factory, event_factory, gamma_user_factory,
):
    """
    A user whose done-events already cover every listed block is granted on recompute;
    blocks outside the set contribute nothing.
    """
    badge = badge_factory()
    badge.rules.set([_block_set_rule(rule_factory, done_configuration, DONE_BLOCKS)])

    user_full = gamma_user_factory()
    for block_id in DONE_BLOCKS:
        _mark_done(event_factory, done_configuration, user_full, block_id)

    user_outside = gamma_user_factory()
    for suffix in 'vwxyz':                    # five done blocks, none in the set
        _mark_done(event_factory, done_configuration, user_outside, f'block-v1:org+A+1+type@done+block@{suffix}')

    result = recompute_holders(badge)

    assert user_full.user_uid in result.granted
    assert user_outside.user_uid not in result.granted
    achievement = Achievement.objects.get(object_id=badge.id, user=user_full)
    assert achievement.all_rules_completed


def test_recompute_writes_partial_block_progress(
    done_configuration, badge_factory, rule_factory, event_factory, gamma_user_factory,
):
    """
    2 of 5 listed blocks done -> in-progress with canonical count/goal (the dashboard
    circle renders floor(2/5*100) = 40%), and a NULL-block_id legacy event never counts.
    """
    badge = badge_factory()
    badge.rules.set([_block_set_rule(rule_factory, done_configuration, DONE_BLOCKS)])

    user = gamma_user_factory()
    _mark_done(event_factory, done_configuration, user, DONE_BLOCKS[0])
    _mark_done(event_factory, done_configuration, user, DONE_BLOCKS[1])
    _mark_done(event_factory, done_configuration, user, None)   # pre-block_id row

    result = recompute_holders(badge)

    assert user.user_uid not in result.granted
    achievement = Achievement.objects.get(object_id=badge.id, user=user)
    assert not achievement.all_rules_completed
    achievement_rule = achievement.achievement_rules.get()
    progress = achievement_rule.dependencies['events'][DONE_EVENT]
    assert progress['count'] == 2
    assert progress['goal'] == 5
