from datetime import datetime
from typing import Optional
import pytest

from achievements.models import Achievement
from badges.tests.factories import BadgeFactory
from badges.models import Badge
from events.tests.factories import EventConfigurationFactory, EventFactory, EventTypeFactory
from events.models import Event, EventConfiguration
from rules.tests.factories import RuleFactory
from rules.models import Rule
from users.models import GammaUser


@pytest.mark.django_db
def setup_event_configuration(
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    event_type_name: str = 'edx_bookmark_added',
    award: int = 1,
) -> EventConfiguration:
    event_configuration = event_configuration_factory(
        event_type=event_type_factory(name=event_type_name),
        award=award
    )
    return event_configuration


@pytest.mark.django_db
def setup_rules(
    rule_factory: RuleFactory,
    event_configuration: EventConfiguration,
    action: Optional[dict] = {},
    filters: Optional[dict] = {}
) -> Rule:
    rules = rule_factory(
        event_configuration=event_configuration,
        action=action,
        filters=filters
    )
    return rules


@pytest.mark.django_db
def setup_badge(badge_factory: BadgeFactory, rules: list) -> Badge:
    badge = badge_factory()
    badge.rules.set(rules)
    return badge


@pytest.mark.django_db
def imitate_signal_dispatch(
    event_factory: EventFactory,
    event_configuration: EventConfiguration,
    username: str = 'test_gamma_user'
) -> Event:
    """
    Create event to dispatch appropriate signal.
    """
    return event_factory(username=username, configuration=event_configuration)


@pytest.mark.django_db
def test_receiving_badge_one_rule_one_event(
    badge_factory: BadgeFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
) -> None:
    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)
    rules = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 1}})
    setup_badge(badge_factory, [rules])

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        'edx_bookmark_added': {'title': f'{event_configuration.title}', 'points': 1}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': 1}
        ]
    }

    imitate_signal_dispatch(event_factory, event_configuration)

    achievements = Achievement.objects.all()

    # Achievements states
    assert achievements.count() == 1
    assert achievements[0].achievement_dependencies[0]['is_achieved'] is True
    assert achievements[0].achievement_dependencies[0]['events']['edx_bookmark_added']['goal'] == 1
    assert achievements[0].achievement_dependencies[0]['events']['edx_bookmark_added']['count'] == 1
    assert achievements[0].all_rules_completed is True

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == 1
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_status,expected_count,expected_goal,user_points', [
    (1, False, 1, 3, 1),
    (2, False, 2, 3, 2),
    (3, True, 3, 3, 3),
])
def test_receiving_badge_one_rule_required_tree_events(
    signals_count: int,
    expected_status: bool,
    expected_count: int,
    expected_goal: int,
    user_points: int,
    badge_factory: BadgeFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
) -> None:
    """
    Test Badge with one rule receiving.

    Badge's details:
        - Badge requires 3 `edx_bookmark_added` events;
    """
    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)
    rules = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 3}})
    setup_badge(badge_factory, [rules])

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        'edx_bookmark_added': {'title': f'{event_configuration.title}', 'points': user_points}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': user_points}
        ]
    }

    for signal in range(signals_count):
        imitate_signal_dispatch(event_factory, event_configuration)

    achievements = Achievement.objects.all()

    # Achievements states
    assert achievements.count() == 1
    assert achievements[0].achievement_dependencies[0]['is_achieved'] is expected_status
    assert achievements[0].achievement_dependencies[0]['events']['edx_bookmark_added']['goal'] == expected_goal
    assert achievements[0].achievement_dependencies[0]['events']['edx_bookmark_added']['count'] == expected_count
    assert achievements[0].all_rules_completed is expected_status

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_status,all_rules_status,expected_count,expected_goal,user_points', [
    (1, (True, False, False), False, (1, 1, 1), (1, 3, 5), 3),
    (2, (True, False, False), False, (1, 2, 2), (1, 3, 5), 6),
    (3, (True, True, False), False, (1, 3, 3), (1, 3, 5), 9),
    (4, (True, True, False), False, (1, 3, 4), (1, 3, 5), 12),
    (5, (True, True, True), True, (1, 3, 5), (1, 3, 5), 15),
])
def test_receiving_badge_multiple_rules_required_multiple_events(
    signals_count: int,
    expected_status: bool,
    all_rules_status: bool,
    expected_count: int,
    expected_goal: int,
    user_points: int,
    badge_factory: BadgeFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
) -> None:
    """
    Test Badge with multiple rules receiving.

    Badge's details:
        - Badge requires 1 `edx_bookmark_added` event;
        - Badge requires 3 `edx_course_enrollment_activated` events;
        - Badge requires 5 `problem_graded` events;
    """
    event_types = ('edx_bookmark_added', 'edx_course_enrollment_activated', 'problem_graded')
    event_configuration1 = setup_event_configuration(event_type_factory, event_configuration_factory)
    event_configuration2 = setup_event_configuration(
        event_type_factory, event_configuration_factory, event_type_name='edx_course_enrollment_activated'
    )
    event_configuration3 = setup_event_configuration(
        event_type_factory, event_configuration_factory, event_type_name='problem_graded'
    )
    rule1 = setup_rules(rule_factory, event_configuration1, action={'edx_bookmark_added': {'count': 1}})
    rule2 = setup_rules(rule_factory, event_configuration2, action={'edx_course_enrollment_activated': {'count': 3}})
    rule3 = setup_rules(rule_factory, event_configuration3, action={'problem_graded': {'count': 5}})
    setup_badge(badge_factory, [rule1, rule2, rule3])

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        'edx_bookmark_added': {'title': f'{event_configuration1.title}', 'points': user_points / 3},
        'edx_course_enrollment_activated': {'title': f'{event_configuration2.title}', 'points': user_points / 3},
        'problem_graded': {'title': f'{event_configuration3.title}', 'points': user_points / 3}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': user_points}
        ]
    }

    for signal in range(signals_count):
        imitate_signal_dispatch(event_factory, event_configuration1)
        imitate_signal_dispatch(event_factory, event_configuration2)
        imitate_signal_dispatch(event_factory, event_configuration3)

    achievements = Achievement.objects.all()

    # Achievements states
    assert achievements.count() == 1
    assert achievements[0].all_rules_completed is all_rules_status

    for counter, dependency in enumerate(achievements[0].achievement_dependencies):
        assert dependency['is_achieved'] is expected_status[counter]
        assert dependency['events'][event_types[counter]]['goal'] == expected_goal[counter]
        assert dependency['events'][event_types[counter]]['count'] == expected_count[counter]

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_status,all_rules_status,expected_count,expected_goal,user_points', [
    (1, (True, False, False), (True, False, False), (1, 1, 1), (1, 3, 5), 1),
    (2, (True, False, False), (True, False, False), (1, 2, 2), (1, 3, 5), 2),
    (3, (True, True, False), (True, True, False), (1, 3, 3), (1, 3, 5), 3),
    (4, (True, True, False), (True, True, False), (1, 3, 4), (1, 3, 5), 4),
    (5, (True, True, True), (True, True, True), (1, 3, 5), (1, 3, 5), 5),
])
def test_receiving_multiple_badges_with_one_rule_for_each(
    signals_count: int,
    expected_status: bool,
    all_rules_status: bool,
    expected_count: int,
    expected_goal: int,
    user_points: int,
    badge_factory: BadgeFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
) -> None:
    """
    Test multiple Badges receiving.

    Badges details:
        - Badge 1 requires 1 `edx_bookmark_added` event;
        - Badge 2 requires 3 `edx_bookmark_added` events;
        - Badge 3 requires 5 `edx_bookmark_added` events;
    """
    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)
    rule1 = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 1}})
    rule2 = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 3}})
    rule3 = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 5}})
    setup_badge(badge_factory, [rule1])
    setup_badge(badge_factory, [rule2])
    setup_badge(badge_factory, [rule3])

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        'edx_bookmark_added': {'title': f'{event_configuration.title}', 'points': user_points}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': user_points}
        ]
    }

    for signal in range(signals_count):
        imitate_signal_dispatch(event_factory, event_configuration)

    achievements = Achievement.objects.all()

    # Achievements states
    assert achievements.count() == 3

    for counter, achievement in enumerate(achievements):
        assert achievement.achievement_dependencies[0]['is_achieved'] is expected_status[counter]
        assert (
            achievement.achievement_dependencies[0]['events']['edx_bookmark_added']['goal']
            == expected_goal[counter]
        )
        assert (
            achievement.achievement_dependencies[0]['events']['edx_bookmark_added']['count']
            == expected_count[counter]
        )
        assert achievement.all_rules_completed is all_rules_status[counter]

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_status,all_rules_status,expected_count,expected_goal,user_points', [
    (
        1,
        ((True, True, True), (False, False, False), (False, False, False)),
        (True, False, False),
        ((1, 1, 1), (1, 1, 1), (1, 1, 1)),
        ((1, 1, 1), (3, 3, 3), (5, 5, 5)),
        3
    ),
    (
        2,
        ((True, True, True), (False, False, False), (False, False, False)),
        (True, False, False),
        ((1, 1, 1), (2, 2, 2), (2, 2, 2)),
        ((1, 1, 1), (3, 3, 3), (5, 5, 5)),
        6
    ),
    (
        3,
        ((True, True, True), (True, True, True), (False, False, False)),
        (True, True, False),
        ((1, 1, 1), (3, 3, 3), (3, 3, 3)),
        ((1, 1, 1), (3, 3, 3), (5, 5, 5)),
        9
    ),
    (
        4,
        ((True, True, True), (True, True, True), (False, False, False)),
        (True, True, False),
        ((1, 1, 1), (3, 3, 3), (4, 4, 4)),
        ((1, 1, 1), (3, 3, 3), (5, 5, 5)),
        12
    ),
    (
        5,
        ((True, True, True), (True, True, True), (True, True, True)),
        (True, True, True),
        ((1, 1, 1), (3, 3, 3), (5, 5, 5)),
        ((1, 1, 1), (3, 3, 3), (5, 5, 5)),
        15
    ),
])
def test_receiving_multiple_badges_with_multiple_rules_for_each(
    signals_count: int,
    expected_status: bool,
    all_rules_status: bool,
    expected_count: int,
    expected_goal: int,
    user_points: int,
    badge_factory: BadgeFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
) -> None:
    """
    Test multiple Badges with multiple rules receiving.

    Badges details:
        - Badge 1 requires ony by one events: `edx_course_enrollment_activated`,
            `edx_bookmark_added`, `problem_graded`;
        - Badge 2 requires three by three events: `edx_course_enrollment_activated`,
            `edx_bookmark_added`, `problem_graded`;
        - Badge 3 requires five by five events: `edx_course_enrollment_activated`,
            `edx_bookmark_added`, `problem_graded`;
    """
    event_types = ('edx_course_enrollment_activated', 'edx_bookmark_added', 'problem_graded')
    event_configuration_bookmark = setup_event_configuration(event_type_factory, event_configuration_factory)
    event_configuration_enrollment = setup_event_configuration(
        event_type_factory, event_configuration_factory, event_type_name='edx_course_enrollment_activated'
    )
    event_configuration_problem_graded = setup_event_configuration(
        event_type_factory, event_configuration_factory, event_type_name='problem_graded'
    )

    rule_enrollment_1 = setup_rules(
        rule_factory, event_configuration_enrollment, action={'edx_course_enrollment_activated': {'count': 1}}
    )
    rule_enrollment_3 = setup_rules(
        rule_factory, event_configuration_enrollment, action={'edx_course_enrollment_activated': {'count': 3}}
    )
    rule_enrollment_5 = setup_rules(
        rule_factory, event_configuration_enrollment, action={'edx_course_enrollment_activated': {'count': 5}}
    )
    rule_bookmark_1 = setup_rules(
        rule_factory, event_configuration_bookmark, action={'edx_bookmark_added': {'count': 1}}
    )
    rule_bookmark_3 = setup_rules(
        rule_factory, event_configuration_bookmark, action={'edx_bookmark_added': {'count': 3}}
    )
    rule_bookmark_5 = setup_rules(
        rule_factory, event_configuration_bookmark, action={'edx_bookmark_added': {'count': 5}}
    )
    rule_problem_graded_1 = setup_rules(
        rule_factory, event_configuration_problem_graded, action={'problem_graded': {'count': 1}}
    )
    rule_problem_graded_3 = setup_rules(
        rule_factory, event_configuration_problem_graded, action={'problem_graded': {'count': 3}}
    )
    rule_problem_graded_5 = setup_rules(
        rule_factory, event_configuration_problem_graded, action={'problem_graded': {'count': 5}}
    )

    setup_badge(badge_factory, [rule_enrollment_1, rule_bookmark_1, rule_problem_graded_1])
    setup_badge(badge_factory, [rule_enrollment_3, rule_bookmark_3, rule_problem_graded_3])
    setup_badge(badge_factory, [rule_enrollment_5, rule_bookmark_5, rule_problem_graded_5])

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        'edx_course_enrollment_activated': {
            'title': f'{event_configuration_enrollment.title}', 'points': user_points / 3
        },
        'edx_bookmark_added': {'title': f'{event_configuration_bookmark.title}', 'points': user_points / 3},
        'problem_graded': {'title': f'{event_configuration_problem_graded.title}', 'points': user_points / 3}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': user_points}
        ]
    }

    for signal in range(signals_count):
        imitate_signal_dispatch(event_factory, event_configuration_enrollment)
        imitate_signal_dispatch(event_factory, event_configuration_bookmark)
        imitate_signal_dispatch(event_factory, event_configuration_problem_graded)

    achievements = Achievement.objects.all()

    # Achievements states
    assert achievements.count() == 3

    for i, achievement in enumerate(achievements):
        assert achievement.all_rules_completed is all_rules_status[i]

        for j, dependency in enumerate(achievement.achievement_dependencies):
            assert dependency['is_achieved'] is expected_status[i][j]
            assert dependency['events'][event_types[j]]['goal'] == expected_goal[i][j]
            assert dependency['events'][event_types[j]]['count'] == expected_count[i][j]

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_status,all_rules_status,expected_count,expected_goal,user_points', [
    (1, (True, False, False), (True, False, False), (1, 1, 1), (1, 3, 5), 1),
    (2, (True, False, False), (True, False, False), (1, 2, 2), (1, 3, 5), 2),
    (3, (True, True, False), (True, True, False), (1, 3, 3), (1, 3, 5), 3),
    (4, (True, True, False), (True, True, False), (1, 3, 4), (1, 3, 5), 4),
    (5, (True, True, True), (True, True, True), (1, 3, 5), (1, 3, 5), 5),
])
def test_receiving_multiple_badges_for_two_users(
    signals_count: int,
    expected_status: bool,
    all_rules_status: bool,
    expected_count: int,
    expected_goal: int,
    user_points: int,
    badge_factory: BadgeFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
) -> None:
    """
    Test multiple Badges receiving.

    Badges details:
        - Badge 1 requires 1 `edx_bookmark_added` event;
        - Badge 2 requires 3 `edx_bookmark_added` events;
        - Badge 3 requires 5 `edx_bookmark_added` events;
    """
    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)
    rule1 = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 1}})
    rule2 = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 3}})
    rule3 = setup_rules(rule_factory, event_configuration, action={'edx_bookmark_added': {'count': 5}})
    setup_badge(badge_factory, [rule1])
    setup_badge(badge_factory, [rule2])
    setup_badge(badge_factory, [rule3])
    first_user = 'first_user'
    second_user = 'second_user'

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        'edx_bookmark_added': {'title': f'{event_configuration.title}', 'points': user_points}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': user_points}
        ]
    }

    for signal in range(signals_count):
        imitate_signal_dispatch(event_factory, event_configuration, username=first_user)
        imitate_signal_dispatch(event_factory, event_configuration, username=second_user)

    achievements_first_user = Achievement.objects.filter(user__user_uid=first_user)
    achievements_second_user = Achievement.objects.filter(user__user_uid=second_user)

    # Achievements states for the `first_user`
    assert achievements_first_user.count() == 3

    for counter, achievement in enumerate(achievements_first_user):
        assert achievement.achievement_dependencies[0]['is_achieved'] is expected_status[counter]
        assert (
            achievement.achievement_dependencies[0]['events']['edx_bookmark_added']['goal']
            == expected_goal[counter]
        )
        assert (
            achievement.achievement_dependencies[0]['events']['edx_bookmark_added']['count']
            == expected_count[counter]
        )
        assert achievement.all_rules_completed is all_rules_status[counter]

    # Achievements states for the `second_user`
    assert achievements_first_user.count() == 3

    for counter, achievement in enumerate(achievements_second_user):
        assert achievement.achievement_dependencies[0]['is_achieved'] is expected_status[counter]
        assert (
            achievement.achievement_dependencies[0]['events']['edx_bookmark_added']['goal']
            == expected_goal[counter]
        )
        assert (
            achievement.achievement_dependencies[0]['events']['edx_bookmark_added']['count']
            == expected_count[counter]
        )
        assert achievement.all_rules_completed is all_rules_status[counter]

    # Gamma User states
    gamma_users = GammaUser.objects.all()

    for gamma_user in gamma_users:
        assert gamma_user.points == user_points
        assert gamma_user.chart == expected_gamma_user_chart
        assert gamma_user.progress == expected_gamma_user_progress
