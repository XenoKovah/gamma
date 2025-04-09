from datetime import datetime
import pytest

from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement, AchievementRule
from avatars.factories import AvatarFactory
from avatars.models import Avatar
from events.factories import EventConfigurationFactory, EventFactory, EventTypeFactory
from events.models import Event, EventConfiguration
from rules.factories import RuleFactory
from rules.models import Rule


@pytest.mark.django_db
def setup_event_configuration(
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    content_type: ContentType = None,
    is_depends_on_achievement: bool = False,
    event_type_name: str = 'rgg.avatar_acquired',
) -> EventConfiguration:
    event_configuration = event_configuration_factory(
        event_type=event_type_factory(name=event_type_name),
        is_depends_on_achievement=is_depends_on_achievement,
        content_type=content_type,
    )
    return event_configuration


@pytest.mark.django_db
def setup_rules(
    rule_factory: RuleFactory,
    event_configuration: EventConfiguration,
    action: dict,
    filters: dict
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
def test_non_dependent_avatar_receive(
    avatar_factory: AvatarFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
):
    event_configuration = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.course_enroll_event'
    )
    rules = setup_rules(
        rule_factory,
        event_configuration,
        action={
            'edx.course_enroll_event': 1
        },
        filters={'fake_filter': 0}
    )

    avatar = setup_avatar(avatar_factory, [rules])

    event = imitate_signal_dispatch(event_factory, event_configuration)

    achievement = Achievement.objects.all()
    achievement_rules = AchievementRule.objects.all()

    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    expected_gamma_user_chart = {
        str(event.event_name): {'title': f'{event_configuration.title}', 'points': event_configuration.award}
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': event_configuration.award}
        ]
    }

    assert achievement.count() == 1
    assert achievement_rules.count() == 1

    assert achievement.first().content_type == ContentType.objects.get_for_model(Avatar)
    assert achievement.first().content_object == avatar

    assert achievement_rules.first().rule == rules
    assert achievement_rules.first().achievement == achievement.first()
    assert len(achievement_rules.first().dependencies['events']) == 1
    assert achievement_rules.first().dependencies['events'][event.event_name]['count'] == 1
    assert achievement_rules.first().dependencies['events'][event.event_name]['goal'] == 1
    assert achievement_rules.first().points == event.configuration.award
    assert achievement_rules.first().status == AchievementRule.Statuses.COMPLETED

    assert achievement.first().user.user_uid == event.username
    assert achievement.first().user.points == event.configuration.award
    assert achievement.first().user.chart == expected_gamma_user_chart
    assert achievement.first().user.progress == expected_gamma_user_progress


@pytest.mark.django_db
def test_non_dependent_avatar_requires_three_events(
    avatar_factory: AvatarFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
):
    event_configuration = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.course_enroll_event'
    )
    rules = setup_rules(
        rule_factory,
        event_configuration,
        action={
            'edx.course_enroll_event': 3
        },
        filters={'fake_filter': 0}
    )

    avatar = setup_avatar(avatar_factory, [rules])
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # first event processing and checking states
    event1 = imitate_signal_dispatch(event_factory, event_configuration)

    expected_gamma_user_chart = {
        str(event_configuration.event_name): {
            'title': f'{event_configuration.title}', 'points': event_configuration.award
        }
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': event_configuration.award}
        ]
    }

    achievement = Achievement.objects.first()
    achievement_rules = AchievementRule.objects.first()

    assert achievement.content_object == avatar

    assert achievement_rules.rule == rules
    assert achievement_rules.achievement == achievement
    assert len(achievement_rules.dependencies['events']) == 1
    assert achievement_rules.dependencies['events'][event_configuration.event_name]['count'] == 1
    assert achievement_rules.dependencies['events'][event_configuration.event_name]['goal'] == 3
    assert achievement_rules.points == event_configuration.award
    assert achievement_rules.status == AchievementRule.Statuses.ACTIVE

    assert achievement.user.user_uid == event1.username
    assert achievement.user.points == event_configuration.award
    assert achievement.user.chart == expected_gamma_user_chart
    assert achievement.user.progress == expected_gamma_user_progress

    # second event processing and checking states
    event2 = imitate_signal_dispatch(event_factory, event_configuration)

    expected_gamma_user_chart = {
        str(event_configuration.event_name): {
            'title': f'{event_configuration.title}', 'points': event_configuration.award * 2
        }
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': event_configuration.award * 2}
        ]
    }

    achievement.refresh_from_db()
    achievement_rules.refresh_from_db()
    achievement.user.refresh_from_db()

    assert achievement.content_object == avatar

    assert achievement_rules.rule == rules
    assert achievement_rules.achievement == achievement
    assert len(achievement_rules.dependencies['events']) == 1
    assert achievement_rules.dependencies['events'][event_configuration.event_name]['count'] == 2
    assert achievement_rules.dependencies['events'][event_configuration.event_name]['goal'] == 3
    assert achievement_rules.points == event_configuration.award
    assert achievement_rules.status == AchievementRule.Statuses.ACTIVE

    assert achievement.user.user_uid == event2.username
    assert achievement.user.points == event_configuration.award * 2
    assert achievement.user.chart == expected_gamma_user_chart
    assert achievement.user.progress == expected_gamma_user_progress

    # third event processing and checking states
    event3 = imitate_signal_dispatch(event_factory, event_configuration)
    expected_gamma_user_chart = {
        str(event_configuration.event_name): {
            'title': f'{event_configuration.title}', 'points': event_configuration.award * 3
        }
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': event_configuration.award * 3}
        ]
    }

    achievement.refresh_from_db()
    achievement_rules.refresh_from_db()
    achievement.user.refresh_from_db()

    assert achievement.content_object == avatar

    assert achievement_rules.rule == rules
    assert achievement_rules.achievement == achievement
    assert len(achievement_rules.dependencies['events']) == 1
    assert achievement_rules.dependencies['events'][event_configuration.event_name]['count'] == 3
    assert achievement_rules.dependencies['events'][event_configuration.event_name]['goal'] == 3
    assert achievement_rules.points == event_configuration.award
    assert achievement_rules.status == AchievementRule.Statuses.COMPLETED

    assert achievement.user.user_uid == event3.username
    assert achievement.user.points == event_configuration.award * 3
    assert achievement.user.chart == expected_gamma_user_chart
    assert achievement.user.progress == expected_gamma_user_progress


@pytest.mark.django_db
def test_non_dependent_avatar_requires_different_events(
    avatar_factory: AvatarFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
):
    event_configuration_1 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.course_enroll_event'
    )
    rule_1 = setup_rules(
        rule_factory,
        event_configuration_1,
        action={
            'edx.course_enroll_event': 2
        },
        filters={'fake_filter': 0}
    )

    event_configuration_2 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.bookmark_added'
    )
    rule_2 = setup_rules(
        rule_factory,
        event_configuration_2,
        action={
            'edx.bookmark_added': 2
        },
        filters={'fake_filter': 0}
    )

    avatar = setup_avatar(avatar_factory, [rule_1, rule_2])
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # first event `edx.course_enroll_event` processing and checking states
    course_enroll_event_1 = imitate_signal_dispatch(event_factory, event_configuration_1)

    expected_gamma_user_chart = {
        str(event_configuration_1.event_name): {
            'title': f'{event_configuration_1.title}', 'points': event_configuration_1.award
        }
    }
    expected_gamma_user_progress = {
        str(date.year): [
            {'date': date.isoformat(), 'points': event_configuration_1.award}
        ]
    }

    achievement = Achievement.objects.first()
    achievement_rules_1 = AchievementRule.objects.first()
    achievement_rules_2 = AchievementRule.objects.last()
    achievement.user.refresh_from_db()

    assert achievement.content_object == avatar

    assert achievement_rules_1.rule == rule_1
    assert achievement_rules_2.rule == rule_2
    assert achievement_rules_1.achievement == achievement
    assert achievement_rules_2.achievement == achievement
    assert len(achievement_rules_1.dependencies['events']) == 1
    assert len(achievement_rules_2.dependencies['events']) == 1
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['count'] == 1
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['goal'] == 2
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['count'] == 0
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['goal'] == 2

    assert achievement_rules_1.points == event_configuration_1.award
    assert achievement_rules_1.status == AchievementRule.Statuses.ACTIVE
    assert achievement_rules_2.points == event_configuration_2.award
    assert achievement_rules_2.status == AchievementRule.Statuses.ACTIVE

    assert achievement.user.user_uid == course_enroll_event_1.username
    assert achievement.user.points == event_configuration_1.award
    assert achievement.user.chart == expected_gamma_user_chart
    assert achievement.user.progress == expected_gamma_user_progress

    # second event `edx.bookmark_added` processing and checking states
    bookmark_added_event_1 = imitate_signal_dispatch(event_factory, event_configuration_2)

    expected_gamma_user_chart.update(
        {
            str(event_configuration_2.event_name): {
                'title': f'{event_configuration_2.title}', 'points': event_configuration_2.award
            }
        }
    )
    expected_gamma_user_progress.update(
        {
            str(date.year): [
                {'date': date.isoformat(), 'points': event_configuration_1.award + event_configuration_2.award}
            ]
        }
    )

    achievement.refresh_from_db()
    achievement_rules_1.refresh_from_db()
    achievement_rules_2.refresh_from_db()

    assert achievement.content_object == avatar

    assert achievement_rules_1.rule == rule_1
    assert achievement_rules_2.rule == rule_2
    assert achievement_rules_1.achievement == achievement
    assert achievement_rules_2.achievement == achievement
    assert len(achievement_rules_1.dependencies['events']) == 1
    assert len(achievement_rules_2.dependencies['events']) == 1
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['count'] == 1
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['goal'] == 2
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['count'] == 1
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['goal'] == 2

    assert achievement_rules_1.points == event_configuration_1.award
    assert achievement_rules_1.status == AchievementRule.Statuses.ACTIVE
    assert achievement_rules_2.points == event_configuration_2.award
    assert achievement_rules_2.status == AchievementRule.Statuses.ACTIVE

    assert achievement.user.user_uid == bookmark_added_event_1.username
    assert achievement.user.points == event_configuration_1.award + event_configuration_2.award
    assert achievement.user.chart == expected_gamma_user_chart
    assert achievement.user.progress == expected_gamma_user_progress

    # third event `edx.course_enroll_event` processing and checking states
    course_enroll_event_2 = imitate_signal_dispatch(event_factory, event_configuration_1)

    expected_gamma_user_chart.update(
        {
            str(event_configuration_1.event_name): {
                'title': f'{event_configuration_1.title}', 'points': event_configuration_1.award * 2
            }
        }
    )
    expected_gamma_user_progress.update(
        {
            str(date.year): [
                {'date': date.isoformat(), 'points': event_configuration_1.award * 2 + event_configuration_2.award}
            ]
        }
    )

    achievement.refresh_from_db()
    achievement_rules_1.refresh_from_db()
    achievement_rules_2.refresh_from_db()

    assert achievement.content_object == avatar

    assert achievement_rules_1.rule == rule_1
    assert achievement_rules_2.rule == rule_2
    assert achievement_rules_1.achievement == achievement
    assert achievement_rules_2.achievement == achievement
    assert len(achievement_rules_1.dependencies['events']) == 1
    assert len(achievement_rules_2.dependencies['events']) == 1
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['count'] == 2
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['goal'] == 2
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['count'] == 1
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['goal'] == 2

    assert achievement_rules_1.points == event_configuration_1.award
    assert achievement_rules_1.status == AchievementRule.Statuses.COMPLETED
    assert achievement_rules_2.points == event_configuration_2.award
    assert achievement_rules_2.status == AchievementRule.Statuses.ACTIVE

    assert achievement.user.user_uid == course_enroll_event_2.username
    assert achievement.user.points == event_configuration_1.award * 2 + event_configuration_2.award
    assert achievement.user.chart == expected_gamma_user_chart
    assert achievement.user.progress == expected_gamma_user_progress

    # fourth event `edx.bookmark_added` processing and checking states
    bookmark_added_event_2 = imitate_signal_dispatch(event_factory, event_configuration_2)

    expected_gamma_user_chart.update(
        {
            str(event_configuration_2.event_name): {
                'title': f'{event_configuration_2.title}', 'points': event_configuration_2.award * 2
            }
        }
    )
    expected_gamma_user_progress.update(
        {
            str(date.year): [
                {'date': date.isoformat(), 'points': event_configuration_1.award * 2 + event_configuration_2.award * 2}
            ]
        }
    )

    achievement.refresh_from_db()
    achievement_rules_1.refresh_from_db()
    achievement_rules_2.refresh_from_db()

    assert achievement.content_object == avatar

    assert achievement_rules_1.rule == rule_1
    assert achievement_rules_2.rule == rule_2
    assert achievement_rules_1.achievement == achievement
    assert achievement_rules_2.achievement == achievement
    assert len(achievement_rules_1.dependencies['events']) == 1
    assert len(achievement_rules_2.dependencies['events']) == 1
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['count'] == 2
    assert achievement_rules_1.dependencies['events'][event_configuration_1.event_name]['goal'] == 2
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['count'] == 2
    assert achievement_rules_2.dependencies['events'][event_configuration_2.event_name]['goal'] == 2

    assert achievement_rules_1.points == event_configuration_1.award
    assert achievement_rules_1.status == AchievementRule.Statuses.COMPLETED
    assert achievement_rules_2.points == event_configuration_2.award
    assert achievement_rules_2.status == AchievementRule.Statuses.COMPLETED

    assert achievement.user.user_uid == bookmark_added_event_2.username
    assert achievement.user.points == event_configuration_1.award * 2 + event_configuration_2.award * 2
    assert achievement.user.chart == expected_gamma_user_chart
    assert achievement.user.progress == expected_gamma_user_progress


@pytest.mark.django_db
def test_processing_dependent_avatrs(
    avatar_factory: AvatarFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
):
    event_configuration_1 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.course_enroll_event'
    )
    rule_1 = setup_rules(
        rule_factory,
        event_configuration_1,
        action={
            'edx.course_enroll_event': 1
        },
        filters={'fake_filter': 0}
    )
    avatar_level_1 = setup_avatar(avatar_factory, [rule_1])

    event_configuration_2 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='gamma.avatar_level_1',
        is_depends_on_achievement=True,
        content_type=ContentType.objects.get_for_model(Avatar)
    )
    rule_2 = setup_rules(
        rule_factory,
        event_configuration_2,
        action={
            'gamma.avatar_level_1': avatar_level_1.id
        },
        filters={'fake_filter': 0}
    )

    event_configuration_3 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.bookmark_added'
    )
    rule_3 = setup_rules(
        rule_factory,
        event_configuration_3,
        action={
            'edx.bookmark_added': 1
        },
        filters={'fake_filter': 0}
    )
    avatar_level_2 = setup_avatar(avatar_factory, [rule_2, rule_3])

    # first event `edx.course_enroll_event` processing and checking states
    imitate_signal_dispatch(event_factory, event_configuration_1)

    achievements = Achievement.objects.all()
    achievement_rules = AchievementRule.objects.all()

    assert len(achievements) == 1
    assert len(achievement_rules) == 1

    assert achievements[0].content_object == avatar_level_1
    assert achievement_rules[0].dependencies['events'][event_configuration_1.event_name]['count'] == 1
    assert achievement_rules[0].dependencies['events'][event_configuration_1.event_name]['goal'] == 1
    assert achievement_rules[0].status == AchievementRule.Statuses.COMPLETED

    # second event `gamma.avatar_level_1` processing and checking states
    imitate_signal_dispatch(event_factory, event_configuration_2)

    achievement_avatar_level_1 = Achievement.objects.first()
    achievement_avatar_level_2 = Achievement.objects.last()
    achievement_rules_avatar_level_1 = AchievementRule.objects.filter(achievement=achievement_avatar_level_1).first()
    achievement_rules_avatar_level_2 = AchievementRule.objects.filter(achievement=achievement_avatar_level_2)

    assert achievement_avatar_level_1.content_object == avatar_level_1
    assert achievement_avatar_level_2.content_object == avatar_level_2

    assert achievement_rules_avatar_level_1.dependencies['events'][event_configuration_1.event_name]['count'] == 1
    assert achievement_rules_avatar_level_1.dependencies['events'][event_configuration_1.event_name]['goal'] == 1
    assert achievement_rules_avatar_level_1.status == AchievementRule.Statuses.COMPLETED

    assert achievement_rules_avatar_level_2[0].status == AchievementRule.Statuses.COMPLETED

    assert achievement_rules_avatar_level_2[1].dependencies['events'][event_configuration_3.event_name]['count'] == 0
    assert achievement_rules_avatar_level_2[1].dependencies['events'][event_configuration_3.event_name]['goal'] == 1
    assert achievement_rules_avatar_level_2[1].status == AchievementRule.Statuses.ACTIVE

    # third event `edx.bookmark_added` processing and checking states
    imitate_signal_dispatch(event_factory, event_configuration_3)

    achievement_avatar_level_1.refresh_from_db()
    achievement_avatar_level_2.refresh_from_db()
    achievement_rules_avatar_level_1 = AchievementRule.objects.filter(achievement=achievement_avatar_level_1).first()
    achievement_rules_avatar_level_2 = AchievementRule.objects.filter(achievement=achievement_avatar_level_2)

    assert achievement_avatar_level_1.content_object == avatar_level_1
    assert achievement_avatar_level_2.content_object == avatar_level_2

    assert achievement_rules_avatar_level_1.dependencies['events'][event_configuration_1.event_name]['count'] == 1
    assert achievement_rules_avatar_level_1.dependencies['events'][event_configuration_1.event_name]['goal'] == 1
    assert achievement_rules_avatar_level_1.status == AchievementRule.Statuses.COMPLETED

    assert achievement_rules_avatar_level_2[0].status == AchievementRule.Statuses.COMPLETED

    assert achievement_rules_avatar_level_2[1].dependencies['events'][event_configuration_3.event_name]['count'] == 1
    assert achievement_rules_avatar_level_2[1].dependencies['events'][event_configuration_3.event_name]['goal'] == 1
    assert achievement_rules_avatar_level_2[1].status == AchievementRule.Statuses.COMPLETED


@pytest.mark.django_db
def test_processing_dependent_avatars_with_arbitrary_events_receiving(
    avatar_factory: AvatarFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
):
    event_configuration_1 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.course_enroll_event'
    )
    rule_1 = setup_rules(
        rule_factory,
        event_configuration_1,
        action={
            'edx.course_enroll_event': 1
        },
        filters={'fake_filter': 0}
    )
    avatar_level_1 = setup_avatar(avatar_factory, [rule_1])

    event_configuration_2 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='gamma.avatar_level_1',
        is_depends_on_achievement=True,
        content_type=ContentType.objects.get_for_model(Avatar)
    )
    rule_2 = setup_rules(
        rule_factory,
        event_configuration_2,
        action={
            'gamma.avatar_level_1': avatar_level_1.id
        },
        filters={'fake_filter': 0}
    )

    event_configuration_3 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='edx.bookmark_added'
    )
    rule_3 = setup_rules(
        rule_factory,
        event_configuration_3,
        action={
            'edx.bookmark_added': 1
        },
        filters={'fake_filter': 0}
    )
    avatar_level_2 = setup_avatar(avatar_factory, [rule_2, rule_3])

    event_configuration_4 = setup_event_configuration(
        event_type_factory,
        event_configuration_factory,
        event_type_name='gamma.avatar_level_2',
        is_depends_on_achievement=True,
        content_type=ContentType.objects.get_for_model(Avatar)
    )
    rule_4 = setup_rules(
        rule_factory,
        event_configuration_4,
        action={
            'gamma.avatar_level_2': avatar_level_2.id
        },
        filters={'fake_filter': 0}
    )

    avatar_level_3 = setup_avatar(avatar_factory, [rule_4])

    # try to process `gamma.avatar_level_2` with uncompleted previous rules
    # which "Is depends on achievement"
    # we can't receive this `avatar_level_3` Achievement
    imitate_signal_dispatch(event_factory, event_configuration_4)

    achievements = Achievement.objects.all()
    achievement_rules = AchievementRule.objects.all()

    assert len(achievements) == 1
    assert len(achievement_rules) == 1

    assert achievements[0].content_object == avatar_level_3
    assert achievement_rules[0].status == AchievementRule.Statuses.ACTIVE

    # dispatch signals step by step
    imitate_signal_dispatch(event_factory, event_configuration_1)
    imitate_signal_dispatch(event_factory, event_configuration_2)
    imitate_signal_dispatch(event_factory, event_configuration_3)

    achievement_rules_for_avatar_level_3 = AchievementRule.objects.first()
    assert achievement_rules_for_avatar_level_3.status == AchievementRule.Statuses.ACTIVE

    # dispatch `gamma.avatar_level_2` signal again after dependent achievements received
    imitate_signal_dispatch(event_factory, event_configuration_4)

    achievement_rules = AchievementRule.objects.all()

    for achievement_rule in achievement_rules:
        assert achievement_rule.status == AchievementRule.Statuses.COMPLETED
