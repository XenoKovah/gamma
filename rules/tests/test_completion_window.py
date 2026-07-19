from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from achievements.models import Achievement
from badges.models import Badge
from rules.serializers import FiltersSerializer
from rules.services import RulesFilterService

pytestmark = pytest.mark.django_db

CERT_EVENT = 'edx_certificate_created'
ENROLL_EVENT = 'edx_course_enrollment_activated'
ACTIVITY_EVENT = 'edx_done_toggled'

GOLD = {'max_weeks': 2}
SILVER = {'min_weeks': 2, 'max_weeks': 4}
BRONZE = {'min_weeks': 4, 'max_weeks': 12}

COURSE = 'course-v1:OST2+Arch1001+2021_v1'
COURSE_RERUN = 'course-v1:OST2+Arch1001+2024_v1'
LEARNER = 'learner-1'


@pytest.fixture
def window_setup(event_configuration_factory, event_factory, rule_factory):
    """
    Build a class in which ``LEARNER`` did some work and then earned a certificate.

    Returns a helper taking the learner's activity offsets (relative to the certificate,
    as negative timedeltas) and yielding the certificate event plus a rule builder.
    """
    cert_configuration = event_configuration_factory(event_type__name=CERT_EVENT)
    configurations = {
        ACTIVITY_EVENT: event_configuration_factory(event_type__name=ACTIVITY_EVENT),
        ENROLL_EVENT: event_configuration_factory(event_type__name=ENROLL_EVENT),
    }

    def _setup(activity, certified_at=None, course=COURSE):
        certified_at = certified_at or now()
        for event_name, delta, activity_course in activity:
            event_factory(
                configuration=configurations[event_name],
                username=LEARNER,
                course_id=activity_course,
                created_at=certified_at - delta,
            )
        certificate = event_factory(
            configuration=cert_configuration,
            username=LEARNER,
            course_id=course,
            created_at=certified_at,
        )

        def make_rule(window, course_filter=COURSE):
            filters = {'course': course_filter}
            if window is not None:
                filters['completion_window'] = window
            return rule_factory(
                event_configuration=cert_configuration,
                filters=filters,
                action={CERT_EVENT: {'count': 1}},
            )

        return certificate, make_rule

    return _setup


@pytest.mark.parametrize(
    'elapsed, expected_tier',
    [
        (timedelta(days=1), 'gold'),
        (timedelta(days=13, hours=23), 'gold'),
        (timedelta(weeks=2), 'gold'),
        (timedelta(weeks=2, seconds=1), 'silver'),
        (timedelta(weeks=3), 'silver'),
        (timedelta(weeks=4), 'silver'),
        (timedelta(weeks=4, seconds=1), 'bronze'),
        (timedelta(weeks=8), 'bronze'),
        (timedelta(weeks=12), 'bronze'),
        (timedelta(weeks=12, seconds=1), None),
        (timedelta(weeks=52), None),
    ],
    ids=[
        '1 day -> Gold',
        'just under 2 weeks -> Gold',
        'exactly 2 weeks -> Gold (max is inclusive)',
        'a second over 2 weeks -> Silver',
        '3 weeks -> Silver',
        'exactly 4 weeks -> Silver',
        'a second over 4 weeks -> Bronze',
        '8 weeks -> Bronze',
        'exactly 12 weeks -> Bronze',
        'a second over 12 weeks -> nothing',
        'a year -> nothing',
    ],
)
def test_exactly_one_tier_matches_each_pace(window_setup, elapsed, expected_tier):
    """
    Every pace resolves to at most one tier: the bands must tile without overlapping.
    """
    certificate, make_rule = window_setup([(ACTIVITY_EVENT, elapsed, COURSE)])
    rules = {tier: make_rule(window) for tier, window in (('gold', GOLD), ('silver', SILVER), ('bronze', BRONZE))}

    service = RulesFilterService(certificate)
    matched = [tier for tier, rule in rules.items() if service.does_event_pass_filters(rule)]

    assert matched == ([expected_tier] if expected_tier else [])


def test_enrolment_never_anchors_the_window(window_setup):
    """
    Enrolling long before starting must not cost the learner their tier.
    """
    certificate, make_rule = window_setup([
        (ENROLL_EVENT, timedelta(weeks=40), COURSE),   # enrolled ages ago, sat idle
        (ACTIVITY_EVENT, timedelta(days=3), COURSE),   # actually started 3 days ago
    ])

    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(GOLD)) is True
    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(BRONZE)) is False


def test_multi_run_class_anchors_on_the_earliest_run(window_setup):
    """
    A class listing several runs is one class: work in the older run anchors the window.
    """
    certificate, make_rule = window_setup(
        [(ACTIVITY_EVENT, timedelta(weeks=6), COURSE_RERUN)],
        course=COURSE,
    )
    both_runs = [COURSE, COURSE_RERUN]

    service = RulesFilterService(certificate)
    assert service.does_event_pass_filters(make_rule(BRONZE, course_filter=both_runs)) is True
    assert service.does_event_pass_filters(make_rule(GOLD, course_filter=both_runs)) is False

    # Scoped to the certificate's run alone, the older run's work is invisible and the
    # window is unverifiable, so no tier is awarded.
    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(BRONZE)) is False


def test_no_prior_activity_fails_closed(window_setup):
    """
    Without recorded work before the certificate the pace is unknown: award nothing.
    """
    certificate, make_rule = window_setup([])

    service = RulesFilterService(certificate)
    assert [w for w in (GOLD, SILVER, BRONZE) if service.does_event_pass_filters(make_rule(w))] == []


def test_activity_after_the_certificate_is_ignored(window_setup):
    """
    Only work preceding the certificate counts, so elapsed time can never go negative.
    """
    certificate, make_rule = window_setup([(ACTIVITY_EVENT, timedelta(days=-5), COURSE)])

    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(GOLD)) is False


def test_rule_without_a_window_is_unaffected(window_setup):
    """
    Rules carrying no completion_window keep their previous behaviour.
    """
    certificate, make_rule = window_setup([])

    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(None)) is True


def test_anchor_lookup_is_cached_across_tiers(window_setup, django_assert_num_queries):
    """
    Judging one certificate against three tiers must not repeat the history lookup.
    """
    certificate, make_rule = window_setup([(ACTIVITY_EVENT, timedelta(days=3), COURSE)])
    rules = [make_rule(GOLD), make_rule(SILVER), make_rule(BRONZE)]

    service = RulesFilterService(certificate)
    with django_assert_num_queries(1):
        for rule in rules:
            service.does_event_pass_filters(rule)


@pytest.mark.parametrize(
    'window, is_valid',
    [
        ({'max_weeks': 2}, True),
        ({'min_weeks': 2, 'max_weeks': 4}, True),
        ({'min_weeks': 0, 'max_weeks': 12}, True),
        ({}, False),
        ({'min_weeks': 4, 'max_weeks': 4}, False),
        ({'min_weeks': 6, 'max_weeks': 2}, False),
        ({'max_weeks': 0}, False),
        ({'min_weeks': -1, 'max_weeks': 2}, False),
        ({'max_weeks': 'soon'}, False),
    ],
    ids=[
        'upper bound only',
        'a full band',
        'zero lower bound',
        'empty window rejected',
        'equal bounds rejected (empty band)',
        'inverted bounds rejected',
        'zero upper bound rejected',
        'negative lower bound rejected',
        'non-numeric rejected',
    ],
)
def test_completion_window_validation(window, is_valid):
    serializer = FiltersSerializer(data={'course': COURSE, 'completion_window': window})

    assert serializer.is_valid() is is_valid


@pytest.mark.parametrize(
    'elapsed, expected_tier, expected_points',
    [
        (timedelta(days=4), 'gold', 28500),
        (timedelta(weeks=3), 'silver', 14250),
        (timedelta(weeks=9), 'bronze', 7125),
        (timedelta(weeks=20), None, 0),
    ],
    ids=['fast -> Gold', 'middling -> Silver', 'slow -> Bronze', 'too slow -> nothing'],
)
def test_tiers_award_exactly_one_badge_through_the_real_pipeline(
    event_configuration_factory,
    event_factory,
    rule_factory,
    badge_factory,
    gamma_user_factory,
    elapsed,
    expected_tier,
    expected_points,
):
    """
    End-to-end: a certificate drives the real signal pipeline and lands on one tier only.

    The three tiers sit on the same class and the same certificate event, so this is the
    check that matters — that the bands cannot double-award, and that a learner slower
    than the widest band simply earns nothing.
    """
    cert_configuration = event_configuration_factory(event_type__name=CERT_EVENT, award=50)
    activity_configuration = event_configuration_factory(event_type__name=ACTIVITY_EVENT, award=0)

    tiers = {}
    for tier, window, points in (('gold', GOLD, 28500), ('silver', SILVER, 14250), ('bronze', BRONZE, 7125)):
        rule = rule_factory(
            event_configuration=cert_configuration,
            action={CERT_EVENT: {'count': 1}},
            filters={'course': COURSE, 'completion_window': window},
        )
        tiers[tier] = badge_factory(set_rules=rule, points=points, is_active=True)

    user = gamma_user_factory()
    certified_at = now()
    points_before = user.points

    event_factory(
        configuration=activity_configuration,
        username=user.user_uid,
        course_id=COURSE,
        created_at=certified_at - elapsed,
    )
    event_factory(
        configuration=cert_configuration,
        username=user.user_uid,
        course_id=COURSE,
        created_at=certified_at,
    )

    badge_type = ContentType.objects.get_for_model(Badge)
    earned = [
        tier for tier, badge in tiers.items()
        if Achievement.objects.filter(
            user=user, content_type=badge_type, object_id=badge.id, completed_at__isnull=False,
        ).exists()
    ]

    assert earned == ([expected_tier] if expected_tier else [])

    # The winning tier's completion points are paid exactly once. Event awards land on
    # the user too, so compare the delta attributable to the badge.
    user.refresh_from_db()
    event_awards = cert_configuration.award + activity_configuration.award
    assert user.points - points_before - event_awards == expected_points


def test_completion_window_survives_serialisation():
    """
    Undeclared keys are dropped by FiltersSerializer, so the window must round-trip intact.
    """
    serializer = FiltersSerializer(data={'course': COURSE, 'completion_window': SILVER})
    assert serializer.is_valid(), serializer.errors

    assert serializer.validated_data['completion_window'] == SILVER
