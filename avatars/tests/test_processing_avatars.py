from datetime import datetime
from typing import List, Optional, Tuple
import pytest

from achievements.models import Achievement
from avatars.factories import AvatarFactory, AvatarSetFactory, UserAvatarConfigFactory
from avatars.models import Avatar, AvatarSet
from events.enums import RggInternalEventTypes
from events.factories import EventConfigurationFactory, EventFactory, EventTypeFactory
from events.models import Event, EventConfiguration
from rules.factories import RuleFactory
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
def setup_avatar(avatar_factory: AvatarFactory, rules: list) -> Avatar:
    avatar = avatar_factory()
    avatar.rules.set(rules)
    return avatar


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
def setup_avatar_set(
    avatar_factory: AvatarFactory,
    avatar_set_factory: AvatarSetFactory,
    rule_factory: RuleFactory,
    stages: int = 5,
    points: int = 1,
    points_range: int = 1,
) -> AvatarSet:
    avatars_list = []
    current_points = points
    event_configuration = EventConfiguration.objects.get(
        event_type__name=RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value
    )

    for stage in range(stages):
        rule = setup_rules(
            rule_factory=rule_factory,
            event_configuration=event_configuration,
            action={RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value: {'points': current_points}}
        )
        avatar = setup_avatar(avatar_factory, [rule])
        avatar.stage = stage + 1
        avatar.save()
        avatars_list.append(avatar)
        current_points += points_range

    avatar_set = avatar_set_factory(is_draft=False)
    avatar_set.avatars.set(avatars_list)

    return avatar_set


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_statuses,expected_counts,expected_goals,user_points', [
    (1, [True, False, False, False, False], [1, 1, 1, 1, 1], [1, 2, 3, 4, 5], 1),
    (2, [True, True, False, False, False], [1, 2, 2, 2, 2], [1, 2, 3, 4, 5], 2),
    (3, [True, True, True, False, False], [1, 2, 3, 3, 3], [1, 2, 3, 4, 5], 3),
    (4, [True, True, True, True, False], [1, 2, 3, 4, 4], [1, 2, 3, 4, 5], 4),
    (5, [True, True, True, True, True], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 5),
])
def test_five_stages_avatar_set_one_point_per_stage(
    signals_count: int,
    expected_statuses: List[bool],
    expected_counts: List[int],
    expected_goals: List[int],
    user_points: int,
    avatar_factory: AvatarFactory,
    avatar_set_factory: AvatarSetFactory,
    rule_factory: RuleFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
) -> None:
    """
    Test 5-stages Avatar Set receiving.

    Avatar Set's details:
        - Avatar Set stages required number of points: 1, 2, 3, 4, 5;
        - The one event `edx_bookmark_added` brings one point;
    """
    stages = 5
    initial_points_count = 1
    points_range = 1

    setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages,
        points=initial_points_count,
        points_range=points_range,
    )

    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)

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

    assert achievements.count() == 5

    # Achievements states
    for stage, achievement in enumerate(achievements):
        assert achievement.achievement_dependencies[0]['is_achieved'] == expected_statuses[stage]
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['goal']
            == expected_goals[stage]
        )
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['count']
            == expected_counts[stage]
        )

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_statuses,expected_counts,expected_goals,user_points', [
    (1, [False, False, False], [1, 1, 1], [3, 6, 9], 1),
    (2, [False, False, False], [2, 2, 2], [3, 6, 9], 2),
    (3, [True, False, False], [3, 3, 3], [3, 6, 9], 3),
    (4, [True, False, False], [3, 4, 4], [3, 6, 9], 4),
    (5, [True, False, False], [3, 5, 5], [3, 6, 9], 5),
    (6, [True, True, False], [3, 6, 6], [3, 6, 9], 6),
    (7, [True, True, False], [3, 6, 7], [3, 6, 9], 7),
    (8, [True, True, False], [3, 6, 8], [3, 6, 9], 8),
    (9, [True, True, True], [3, 6, 9], [3, 6, 9], 9),
])
def test_three_stages_avatar_set_tree_points_per_stage(
    signals_count: int,
    expected_statuses: List[bool],
    expected_counts: List[int],
    expected_goals: List[int],
    user_points: int,
    avatar_factory: AvatarFactory,
    avatar_set_factory: AvatarSetFactory,
    rule_factory: RuleFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
) -> None:
    """
    Test 3-stages Avatar Set receiving.

    Avatar Set's details:
        - Avatar Set stages required number of points: 3, 6, 9;
        - The one event `edx_bookmark_added` brings one point;
    """
    stages = 3
    initial_points_count = 3
    points_range = 3

    setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages,
        points=initial_points_count,
        points_range=points_range,
    )

    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)

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

    assert achievements.count() == 3

    # Achievements states
    for stage, achievement in enumerate(achievements):
        assert achievement.achievement_dependencies[0]['is_achieved'] == expected_statuses[stage]
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['goal']
            == expected_goals[stage]
        )
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['count']
            == expected_counts[stage]
        )

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_statuses,expected_counts,expected_goals,user_points', [
    (1, [False, False, False], [6, 6, 6], [18, 24, 30], 6),
    (2, [False, False, False], [12, 12, 12], [18, 24, 30], 12),
    (3, [True, False, False], [18, 18, 18], [18, 24, 30], 18),
    (4, [True, True, False], [18, 24, 24], [18, 24, 30], 24),
    (5, [True, True, True], [18, 24, 30], [18, 24, 30], 30),
    (6, [True, True, True], [18, 24, 30], [18, 24, 30], 36),
    (7, [True, True, True], [18, 24, 30], [18, 24, 30], 42),
])
def test_three_stages_avatar_set_six_points_per_stage_different_events(
    signals_count: int,
    expected_statuses: List[bool],
    expected_counts: List[int],
    expected_goals: List[int],
    user_points: int,
    avatar_factory: AvatarFactory,
    avatar_set_factory: AvatarSetFactory,
    rule_factory: RuleFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
) -> None:
    """
    Test 3-stages Avatar Set receiving.

    Avatar Set's details:
        - Avatar Set stages required number of points: 18, 24, 30;
        - The one event `edx_bookmark_added` brings 1 point;
        - The one event `stop_video` brings 2 points;
        - The one event `edx_certificate_created` brings 3 points;
    """
    stages = 3
    initial_points_count = 18
    points_range = 6

    setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages,
        points=initial_points_count,
        points_range=points_range,
    )

    event_configuration_bookmark = setup_event_configuration(event_type_factory, event_configuration_factory)
    event_configuration_stop_video = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='stop_video',
        award=2,
    )
    event_configuration_certificate = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx_certificate_created',
        award=3,
    )

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        'edx_bookmark_added': {'title': f'{event_configuration_bookmark.title}', 'points': 1 * signals_count},
        'stop_video': {'title': f'{event_configuration_stop_video.title}', 'points': 2 * signals_count},
        'edx_certificate_created': {'title': f'{event_configuration_certificate.title}', 'points': 3 * signals_count}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': user_points}
        ]
    }

    for signal in range(signals_count):
        imitate_signal_dispatch(event_factory, event_configuration_bookmark)
        imitate_signal_dispatch(event_factory, event_configuration_stop_video)
        imitate_signal_dispatch(event_factory, event_configuration_certificate)

    achievements = Achievement.objects.all()

    assert achievements.count() == 3

    # Achievements states
    for stage, achievement in enumerate(achievements):
        assert achievement.achievement_dependencies[0]['is_achieved'] == expected_statuses[stage]
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['goal']
            == expected_goals[stage]
        )
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['count']
            == expected_counts[stage]
        )

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_statuses,expected_counts,expected_goals,user_points', [
    (
        1,
        ([True, False, False, False, False], [False, False, False, False, False]),
        ([1, 1, 1, 1, 1], [1, 1, 1, 1, 1]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        1
    ),
    (
        2,
        ([True, True, False, False, False], [True, False, False, False, False]),
        ([1, 2, 2, 2, 2], [2, 2, 2, 2, 2]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        2
    ),
    (
        3,
        ([True, True, True, False, False], [True, False, False, False, False]),
        ([1, 2, 3, 3, 3], [2, 3, 3, 3, 3]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        3
    ),
    (
        4,
        ([True, True, True, True, False], [True, True, False, False, False]),
        ([1, 2, 3, 4, 4], [2, 4, 4, 4, 4]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        4
    ),
    (
        5,
        ([True, True, True, True, True], [True, True, False, False, False]),
        ([1, 2, 3, 4, 5], [2, 4, 5, 5, 5]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        5
    ),
    (
        6,
        ([True, True, True, True, True], [True, True, True, False, False]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 6, 6]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        6
    ),
    (
        7,
        ([True, True, True, True, True], [True, True, True, False, False]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 7, 7]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        7
    ),
    (
        8,
        ([True, True, True, True, True], [True, True, True, True, False]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 8]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        8
    ),
    (
        9,
        ([True, True, True, True, True], [True, True, True, True, False]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 9]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        9
    ),
    (
        10,
        ([True, True, True, True, True], [True, True, True, True, True]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
        10
    ),
])
def test_parallel_receiving_achievements_in_two_avatar_sets(
    signals_count: int,
    expected_statuses: List[bool],
    expected_counts: List[int],
    expected_goals: List[int],
    user_points: int,
    avatar_factory: AvatarFactory,
    avatar_set_factory: AvatarSetFactory,
    rule_factory: RuleFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
) -> None:
    """
    Test two parallel 5-stages Avatar Sets receiving.

    Avatar Set's details:
        - Avatar Set 1 stages required number of points: 1, 2, 3, 4, 5;
        - Avatar Set 2 stages required number of points: 2, 4, 6, 8, 10;
        - The one event `edx_bookmark_added` brings one point;
    """
    stages_set1 = 5
    stages_set2 = 5
    initial_points_count_set1 = 1
    initial_points_count_set2 = 2
    points_range_set1 = 1
    points_range_set2 = 2

    avatar_set1 = setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages_set1,
        points=initial_points_count_set1,
        points_range=points_range_set1,
    )
    avatar_set2 = setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages_set2,
        points=initial_points_count_set2,
        points_range=points_range_set2,
    )

    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)

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

    achievements_set1 = Achievement.objects.filter(object_id__in=avatar_set1.avatars.values_list('id', flat=True))
    achievements_set2 = Achievement.objects.filter(object_id__in=avatar_set2.avatars.values_list('id', flat=True))

    assert achievements_set1.count() == 5
    assert achievements_set2.count() == 5

    # Achievements in Avatar Set 1 states
    for stage, achievement in enumerate(achievements_set1):
        assert achievement.achievement_dependencies[0]['is_achieved'] == expected_statuses[0][stage]
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['goal']
            == expected_goals[0][stage]
        )
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['count']
            == expected_counts[0][stage]
        )

    # Achievements in Avatar Set 2 states
    for stage, achievement in enumerate(achievements_set2):
        assert achievement.achievement_dependencies[0]['is_achieved'] == expected_statuses[1][stage]
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['goal']
            == expected_goals[1][stage]
        )
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['count']
            == expected_counts[1][stage]
        )

    # Gamma User states
    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    assert gamma_user.points == user_points
    assert gamma_user.chart == expected_gamma_user_chart
    assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_statuses,expected_counts,expected_goals,user_points', [
    (1, [True, False, False, False, False], [1, 1, 1, 1, 1], [1, 2, 3, 4, 5], 1),
    (2, [True, True, False, False, False], [1, 2, 2, 2, 2], [1, 2, 3, 4, 5], 2),
    (3, [True, True, True, False, False], [1, 2, 3, 3, 3], [1, 2, 3, 4, 5], 3),
    (4, [True, True, True, True, False], [1, 2, 3, 4, 4], [1, 2, 3, 4, 5], 4),
    (5, [True, True, True, True, True], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 5),
])
def test_five_stages_avatar_set_receiving_two_gamma_users(
    signals_count: int,
    expected_statuses: List[bool],
    expected_counts: List[int],
    expected_goals: List[int],
    user_points: int,
    avatar_factory: AvatarFactory,
    avatar_set_factory: AvatarSetFactory,
    rule_factory: RuleFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
) -> None:
    """
    Test 5-stages Avatar Set receiving.

    Avatar Set's details:
        - Avatar Set stages required number of points: 1, 2, 3, 4, 5;
        - The one event `edx_bookmark_added` brings one point;
    """
    stages = 5
    initial_points_count = 1
    points_range = 1
    first_user = 'first_user'
    second_user = 'second_user'

    setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages,
        points=initial_points_count,
        points_range=points_range,
    )

    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)

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

    assert achievements_first_user.count() == 5
    assert achievements_second_user.count() == 5

    # Achievements states for the `first_user`
    for stage, achievement in enumerate(achievements_first_user):
        assert achievement.achievement_dependencies[0]['is_achieved'] == expected_statuses[stage]
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['goal']
            == expected_goals[stage]
        )
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['count']
            == expected_counts[stage]
        )

    # Achievements states for the `second_user`
    for stage, achievement in enumerate(achievements_first_user):
        assert achievement.achievement_dependencies[0]['is_achieved'] == expected_statuses[stage]
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['goal']
            == expected_goals[stage]
        )
        assert (
            achievement.achievement_dependencies[0]['points']['rgg_points_distribution']['count']
            == expected_counts[stage]
        )

    # Gamma Users states
    gamma_users = GammaUser.objects.all()

    for gamma_user in gamma_users:
        assert gamma_user.points == user_points
        assert gamma_user.chart == expected_gamma_user_chart
        assert gamma_user.progress == expected_gamma_user_progress


@pytest.mark.django_db
@pytest.mark.parametrize('signals_count,expected_stages_for_set', [
    (1, (1, None, None)),
    (2, (2, 1, None)),
    (3, (3, 1, 1)),
    (4, (4, 2, 1)),
    (5, (5, 2, 1)),
    (6, (5, 3, 2)),
    (7, (5, 3, 2)),
    (8, (5, 4, 2)),
    (9, (5, 4, 3)),
    (10, (5, 5, 3)),
    (11, (5, 5, 3)),
    (12, (5, 5, 4)),
    (13, (5, 5, 4)),
    (14, (5, 5, 4)),
    (15, (5, 5, 5)),
])
def test_get_last_achieved_user_avatar_in_three_avatar_sets(
    signals_count: int,
    expected_stages_for_set: Tuple[Optional[int]],
    avatar_factory: AvatarFactory,
    avatar_set_factory: AvatarSetFactory,
    user_avatar_config_factory: UserAvatarConfigFactory,
    rule_factory: RuleFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
) -> None:
    """
    Test 3 parallel 5-stages Avatar Sets receiving.

    Avatar Set's details:
        - Avatar Set 1 stages required number of points: 1, 2, 3, 4, 5;
        - Avatar Set 2 stages required number of points: 2, 4, 6, 8, 10;
        - Avatar Set 3 stages required number of points: 3, 6, 9, 12, 15;
        - The one event `edx_bookmark_added` brings one point;
    """
    stages_set_1_2_3 = 5
    initial_points_count_set1 = 1
    initial_points_count_set2 = 2
    initial_points_count_set3 = 3
    points_range_set1 = 1
    points_range_set2 = 2
    points_range_set3 = 3

    avatar_set1 = setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages_set_1_2_3,
        points=initial_points_count_set1,
        points_range=points_range_set1,
    )
    avatar_set2 = setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages_set_1_2_3,
        points=initial_points_count_set2,
        points_range=points_range_set2,
    )
    avatar_set3 = setup_avatar_set(
        avatar_factory,
        avatar_set_factory,
        rule_factory,
        stages=stages_set_1_2_3,
        points=initial_points_count_set3,
        points_range=points_range_set3,
    )

    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)

    for signal in range(signals_count):
        imitate_signal_dispatch(event_factory, event_configuration)

    gamma_user = GammaUser.objects.get(user_uid='test_gamma_user')

    # check current Gamma User's Avatar for each Avatar Set
    user_avatar_config = user_avatar_config_factory(user=gamma_user, avatar_set=avatar_set1)

    for stage, avatar_set in zip(expected_stages_for_set, (avatar_set1, avatar_set2, avatar_set3)):
        user_avatar_config.avatar_set = avatar_set
        user_avatar_config.save()
        current_avatar = user_avatar_config.get_last_achieved_avatar()
        current_stage = getattr(current_avatar, 'stage') if current_avatar else None

        assert current_stage == stage
