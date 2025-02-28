import pytest

from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement, AchievementRule
from avatars.factories import AvatarFactory
from avatars.models import Avatar
from events.factories import EventConfigurationFactory, EventFactory, EventTypeFactory
from events.models import EventConfiguration
from rules.factories import RuleFactory
from rules.models import Rule


@pytest.mark.django_db
def setup_event_configuration(
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory
):
    event_configuration = event_configuration_factory(
        event_type=event_type_factory(name='rgg.avatar_acquired'),
        is_depends_on_achievement=True,
        content_type=ContentType.objects.get_for_model(Avatar),
    )
    return event_configuration


@pytest.mark.django_db
def setup_rules(rule_factory: RuleFactory, event_configuration: EventConfiguration):
    rules = rule_factory(
        event_configuration=event_configuration,
        action={'rgg.avatar_acquired': 1},
        filters={'interval': {'end': '2030-12-20T12:20:12', 'start': '2020-12-20T12:20:12'}}
    )
    return rules


@pytest.mark.django_db
def setup_avatar(avatar_factory: AvatarFactory, rules: Rule):
    avatar = avatar_factory()
    avatar.rules.add(rules)
    return avatar


@pytest.mark.django_db
def imitate_signal_dispatch(
    event_factory: EventFactory,
    event_configuration: EventConfiguration
):
    """
    Create event to dispatch appropriate signal.
    """
    return event_factory(configuration=event_configuration)


@pytest.mark.django_db
def test_avatar_receive(
    avatar_factory: AvatarFactory,
    event_factory: EventFactory,
    event_type_factory: EventTypeFactory,
    event_configuration_factory: EventConfigurationFactory,
    rule_factory: RuleFactory
):
    event_configuration = setup_event_configuration(event_type_factory, event_configuration_factory)
    rules = setup_rules(rule_factory, event_configuration)
    avatar = setup_avatar(avatar_factory, rules)

    event = imitate_signal_dispatch(event_factory, event_configuration)

    achievement = Achievement.objects.all()
    achievement_rules = AchievementRule.objects.all()

    assert achievement.count() == 1
    assert achievement_rules.count() == 1

    assert achievement.first().content_type == ContentType.objects.get_for_model(Avatar)
    assert achievement.first().content_object == avatar

    assert achievement_rules.first().rule == rules
    assert achievement_rules.first().achievement == achievement.first()

    assert achievement.first().user.user_uid == event.username
