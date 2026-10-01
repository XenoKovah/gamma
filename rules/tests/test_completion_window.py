from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils.timezone import now

from achievements.models import Achievement
from badges.models import Badge
from rules.serializers import FiltersSerializer
from rules.services import RulesFilterService
from users.models import GammaUser

pytestmark = pytest.mark.django_db

CERT_EVENT = 'edx_certificate_created'
ENROLL_EVENT = 'edx_course_enrollment_activated'
# A "Mark as complete" click: the only activity that starts a class's clock.
ACTIVITY_EVENT = 'edx_done_toggled'
VIDEO_EVENT = 'stop_video'
PROBLEM_EVENT = 'edx_grades_problem_submitted'
BOOKMARK_EVENT = 'edx_bookmark_added'
FORUM_EVENT = 'edx_forum_thread_created'
NON_CLICK_EVENTS = (VIDEO_EVENT, PROBLEM_EVENT, BOOKMARK_EVENT, FORUM_EVENT, ENROLL_EVENT, CERT_EVENT)

GOLD = {'max_weeks': 2}
SILVER = {'min_weeks': 2, 'max_weeks': 4}
BRONZE = {'min_weeks': 4, 'max_weeks': 12}
PLAIN = {'min_weeks': 12, 'match_without_anchor': True}
ALL_TIERS = (('gold', GOLD), ('silver', SILVER), ('bronze', BRONZE), ('plain', PLAIN))

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
        name: event_configuration_factory(event_type__name=name)
        for name in (ACTIVITY_EVENT, VIDEO_EVENT, PROBLEM_EVENT, BOOKMARK_EVENT, FORUM_EVENT, ENROLL_EVENT)
    }
    configurations[CERT_EVENT] = cert_configuration

    def _setup(activity, certified_at=None, course=COURSE, beta_completion=False):
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
            beta_completion=beta_completion,
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
        (timedelta(weeks=12, seconds=1), 'plain'),
        (timedelta(weeks=52), 'plain'),
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
        'a second over 12 weeks -> Plain',
        'a year -> Plain',
    ],
)
def test_exactly_one_tier_matches_each_pace(window_setup, elapsed, expected_tier):
    """
    Every pace resolves to exactly one tier: the bands must tile without overlapping.
    """
    certificate, make_rule = window_setup([(ACTIVITY_EVENT, elapsed, COURSE)])
    rules = {tier: make_rule(window) for tier, window in ALL_TIERS}

    service = RulesFilterService(certificate)
    matched = [tier for tier, rule in rules.items() if service.does_event_pass_filters(rule)]

    assert matched == [expected_tier]


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


@pytest.mark.parametrize('event_name', NON_CLICK_EVENTS)
def test_only_mark_as_complete_clicks_start_the_clock(window_setup, event_name):
    """
    Videos, answers, bookmarks, forum posts, enrolments and earlier certificates never anchor.

    With nothing but such activity before the certificate the pace is unmeasurable, so
    only the catch-all band claims it. The earlier certificate sits in the other run of
    the class, which the rule's course filter includes.
    """
    certificate, make_rule = window_setup([(event_name, timedelta(days=3), COURSE_RERUN)])
    both_runs = [COURSE, COURSE_RERUN]
    rules = {tier: make_rule(window, course_filter=both_runs) for tier, window in ALL_TIERS}

    service = RulesFilterService(certificate)
    matched = [tier for tier, rule in rules.items() if service.does_event_pass_filters(rule)]

    assert matched == ['plain']


def test_first_click_anchors_even_after_earlier_other_activity(window_setup):
    """
    The clock starts at the first "Mark as complete" click, not at anything done before it.

    A learner who watched videos and answered problems for months and then clicked
    through the class in three days finished in three days.
    """
    certificate, make_rule = window_setup([
        (ENROLL_EVENT, timedelta(weeks=50), COURSE),
        (VIDEO_EVENT, timedelta(weeks=40), COURSE),
        (PROBLEM_EVENT, timedelta(weeks=30), COURSE),
        (FORUM_EVENT, timedelta(weeks=20), COURSE),
        (ACTIVITY_EVENT, timedelta(days=3), COURSE),
        (ACTIVITY_EVENT, timedelta(days=1), COURSE),
    ])
    rules = {tier: make_rule(window) for tier, window in ALL_TIERS}

    service = RulesFilterService(certificate)
    matched = [tier for tier, rule in rules.items() if service.does_event_pass_filters(rule)]

    assert matched == ['gold']


@pytest.mark.skipif(connection.vendor != 'sqlite', reason='reads the SQLite query plan')
def test_anchor_lookup_uses_the_user_course_time_index(window_setup):
    """
    Restricting the anchor to clicks must not cost the (username, course_id, created_at) index.

    The lookup runs inside the learner's row lock on every certificate, against a table of
    millions of rows, so a full scan here would be felt live.
    """
    certificate, make_rule = window_setup([(ACTIVITY_EVENT, timedelta(days=3), COURSE)])
    service = RulesFilterService(certificate)

    with CaptureQueriesContext(connection) as queries:
        service._window_anchor(make_rule(GOLD))  # pylint: disable=protected-access
    [anchor_query] = [q['sql'] for q in queries.captured_queries if 'events_event' in q['sql']]

    with connection.cursor() as cursor:
        cursor.execute('EXPLAIN QUERY PLAN ' + anchor_query)
        plan = ' '.join(str(row) for row in cursor.fetchall())

    assert 'event_user_course_time_idx' in plan


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

    # Scoped to the certificate's run alone, the older run's work is invisible, so the
    # pace reads as unmeasurable and the graded band declines.
    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(BRONZE)) is False


def test_unmeasurable_pace_goes_to_the_catch_all_band_only(window_setup):
    """
    With no recorded work before the certificate, only the catch-all band claims it.

    This is the common case for learners whose activity predates event tracking, so it
    must land on exactly one tier rather than on all of them or none.
    """
    certificate, make_rule = window_setup([])
    rules = {tier: make_rule(window) for tier, window in ALL_TIERS}

    service = RulesFilterService(certificate)
    matched = [tier for tier, rule in rules.items() if service.does_event_pass_filters(rule)]

    assert matched == ['plain']


def test_graded_bands_still_decline_an_unmeasurable_pace(window_setup):
    """
    Without a catch-all in the set, an unmeasurable pace earns nothing at all.
    """
    certificate, make_rule = window_setup([])

    service = RulesFilterService(certificate)
    assert [w for w in (GOLD, SILVER, BRONZE) if service.does_event_pass_filters(make_rule(w))] == []


def test_activity_after_the_certificate_is_ignored(window_setup):
    """
    Only work preceding the certificate counts, so elapsed time can never go negative.

    Later activity cannot anchor, so the pace reads as unmeasurable and falls to the
    catch-all rather than scoring as an instant finish.
    """
    certificate, make_rule = window_setup([(ACTIVITY_EVENT, timedelta(days=-5), COURSE)])

    service = RulesFilterService(certificate)
    assert service.does_event_pass_filters(make_rule(GOLD)) is False
    assert service.does_event_pass_filters(make_rule(PLAIN)) is True


def test_rule_without_a_window_is_unaffected(window_setup):
    """
    Rules carrying no completion_window keep their previous behaviour.
    """
    certificate, make_rule = window_setup([])

    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(None)) is True


def test_history_lookups_are_cached_across_tiers(window_setup):
    """
    Judging one certificate against three tiers must not repeat the anchor or held-tier lookup.
    """
    certificate, make_rule = window_setup([(ACTIVITY_EVENT, timedelta(days=3), COURSE)])
    rules = [make_rule(GOLD), make_rule(SILVER), make_rule(BRONZE)]

    service = RulesFilterService(certificate)
    with CaptureQueriesContext(connection) as queries:
        for rule in rules:
            service.does_event_pass_filters(rule)
    sql = [query['sql'] for query in queries.captured_queries]

    assert sum('events_event' in query for query in sql) == 1  # the anchor
    assert sum('achievements_achievement' in query for query in sql) == 1  # a tier already held


@pytest.mark.parametrize(
    'activity',
    [
        [],
        [(ACTIVITY_EVENT, timedelta(days=3), COURSE)],
        [(ACTIVITY_EVENT, timedelta(weeks=40), COURSE)],
    ],
    ids=['no clicks at all', 'clicked 3 days before', 'clicked 40 weeks before'],
)
def test_beta_completion_is_gold_whatever_the_pace(window_setup, activity):
    """
    A certificate allowlisted for completing the class's beta lands on Gold, and only Gold.

    With no clicks the pace is unmeasurable, which would otherwise mean the Plain
    catch-all; with slow clicks, timing alone would mean Plain too.
    """
    certificate, make_rule = window_setup(activity, beta_completion=True)
    rules = {tier: make_rule(window) for tier, window in ALL_TIERS}

    service = RulesFilterService(certificate)
    matched = [tier for tier, rule in rules.items() if service.does_event_pass_filters(rule)]

    assert matched == ['gold']


def test_beta_completion_leaves_windowless_rules_alone(window_setup):
    """
    Multi-class Accomplishment rules (plain certificate rules, no window) still match.
    """
    certificate, make_rule = window_setup([], beta_completion=True)

    assert RulesFilterService(certificate).does_event_pass_filters(make_rule(None)) is True


def test_a_learner_holding_a_tier_earns_no_second_one(window_setup, achievement_factory, badge_factory):
    """
    A second certificate for a class (another run, or a re-issue) never adds a second tier.

    The learner holds Plain from an earlier certificate. A beta-completion certificate in
    the other run would be Gold on its own, but the class is already tiered. Rules without
    a window are unaffected.
    """
    both_runs = [COURSE, COURSE_RERUN]
    certificate, make_rule = window_setup([], course=COURSE_RERUN, beta_completion=True)
    rules = {tier: make_rule(window, course_filter=both_runs) for tier, window in ALL_TIERS}
    plain = badge_factory(set_rules=rules['plain'])
    user, _ = GammaUser.objects.get_or_create(user_uid=LEARNER)
    achievement_factory(user=user, object_id=plain.id, completed_at=now())

    service = RulesFilterService(certificate)
    assert [tier for tier, rule in rules.items() if service.does_event_pass_filters(rule)] == []
    assert service.does_event_pass_filters(make_rule(None, course_filter=both_runs)) is True


@pytest.mark.parametrize(
    'window, is_valid',
    [
        ({'max_weeks': 2}, True),
        ({'min_weeks': 2, 'max_weeks': 4}, True),
        ({'min_weeks': 0, 'max_weeks': 12}, True),
        ({'min_weeks': 12, 'match_without_anchor': True}, True),
        ({}, False),
        ({'match_without_anchor': True}, False),
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
        'open-ended catch-all band',
        'empty window rejected',
        'catch-all without bounds rejected',
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
        (timedelta(weeks=20), 'plain', 2850),
        (None, 'plain', 2850),
    ],
    ids=[
        'fast -> Gold',
        'middling -> Silver',
        'slow -> Bronze',
        'very slow -> Plain',
        'no prior activity at all -> Plain',
    ],
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
    tier_points = (('gold', GOLD, 28500), ('silver', SILVER, 14250),
                   ('bronze', BRONZE, 7125), ('plain', PLAIN, 2850))
    for tier, window, points in tier_points:
        rule = rule_factory(
            event_configuration=cert_configuration,
            action={CERT_EVENT: {'count': 1}},
            filters={'course': COURSE, 'completion_window': window},
        )
        tiers[tier] = badge_factory(set_rules=rule, points=points, is_active=True)

    user = gamma_user_factory()
    certified_at = now()
    points_before = user.points

    if elapsed is not None:
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

    assert earned == [expected_tier]

    # The winning tier's completion points are paid exactly once. Event awards land on
    # the user too, so compare the delta attributable to the badge.
    user.refresh_from_db()
    event_awards = cert_configuration.award
    if elapsed is not None:
        event_awards += activity_configuration.award
    assert user.points - points_before - event_awards == expected_points


def test_completion_window_survives_serialisation():
    """
    Undeclared keys are dropped by FiltersSerializer, so the window must round-trip intact.
    """
    serializer = FiltersSerializer(data={'course': COURSE, 'completion_window': SILVER})
    assert serializer.is_valid(), serializer.errors

    assert serializer.validated_data['completion_window'] == SILVER


@pytest.fixture
def tiered_class(event_configuration_factory, rule_factory, badge_factory):
    """
    Build the four real tier badges of one class (both runs), on a certificate paying 50 points.
    """
    cert_configuration = event_configuration_factory(event_type__name=CERT_EVENT, award=50)
    tiers = {}
    tier_points = (('gold', GOLD, 28500), ('silver', SILVER, 14250),
                   ('bronze', BRONZE, 7125), ('plain', PLAIN, 2850))
    for tier, window, points in tier_points:
        rule = rule_factory(
            event_configuration=cert_configuration,
            action={CERT_EVENT: {'count': 1}},
            filters={'course': [COURSE, COURSE_RERUN], 'completion_window': window},
        )
        tiers[tier] = badge_factory(set_rules=rule, points=points, is_active=True)
    return cert_configuration, tiers


def _earned_tiers(user, tiers):
    badge_type = ContentType.objects.get_for_model(Badge)
    return [
        tier for tier, badge in tiers.items()
        if Achievement.objects.filter(
            user=user, content_type=badge_type, object_id=badge.id, completed_at__isnull=False,
        ).exists()
    ]


def test_beta_completion_awards_gold_once_through_the_real_pipeline(tiered_class, event_factory, gamma_user_factory):
    """
    End-to-end: a beta completer's certificate, with no clicks at all, earns Gold and is paid once.
    """
    cert_configuration, tiers = tiered_class
    user = gamma_user_factory()
    points_before = user.points

    event_factory(configuration=cert_configuration, username=user.user_uid, course_id=COURSE, beta_completion=True)

    assert _earned_tiers(user, tiers) == ['gold']
    user.refresh_from_db()
    assert user.points - points_before - cert_configuration.award == 28500


def test_second_certificate_keeps_one_tier_through_the_real_pipeline(tiered_class, event_factory, gamma_user_factory):
    """
    End-to-end: a learner already tiered on a class keeps that one tier when certified again.
    """
    cert_configuration, tiers = tiered_class
    user = gamma_user_factory()
    points_before = user.points

    event_factory(configuration=cert_configuration, username=user.user_uid, course_id=COURSE)
    event_factory(
        configuration=cert_configuration, username=user.user_uid, course_id=COURSE_RERUN, beta_completion=True,
    )

    assert _earned_tiers(user, tiers) == ['plain']
    user.refresh_from_db()
    assert user.points - points_before - 2 * cert_configuration.award == 2850
