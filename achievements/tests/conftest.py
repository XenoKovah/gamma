import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from achievements.services import RuleDependencyService

from .constants import mock_event_based_name, mock_achievement_based_name


@pytest.fixture
def achievement_with_events_dependencies(
    rule_factory,
    event_factory,
    badge_factory,
    gamma_user_factory,
    achievement_factory,
    achievement_rule_factory,
):
    def _setup(event_count_mock=1, initial_count=1, goal=3):
        user = gamma_user_factory()
        event = event_factory()
        event_name_mock = event.configuration.event_name
        rule = rule_factory(event_configuration=event.configuration, action={event_name_mock: event_count_mock})
        badge = badge_factory(set_rules=(rule,))

        achievement = achievement_factory(
            user=user,
            content_type=ContentType.objects.get_for_model(type(badge)),
            object_id=badge.id,
            title=badge.title,
            description=badge.description,
        )

        dependencies = {
            'events': {
                event_name_mock: {
                    'count': initial_count,
                    'goal': goal,
                    'last': now().isoformat(),
                }
            }
        }

        achievement_rule_factory(achievement=achievement, rule=rule, dependencies=dependencies)

        return user, event, badge, achievement, event_name_mock

    return _setup


@pytest.fixture
def mock_filters_dict():
    return {
        'org': 'test',
        'course': 'course-v1:test+1+2',
        'frequency': 3
    }


@pytest.fixture
def mock_action_event_based_dict():
    return {mock_event_based_name: 3}


@pytest.fixture
def mock_dependent_badge(badge_factory):
    return badge_factory()


@pytest.fixture
def mock_action_achievement_based_dict(mock_dependent_badge):
    return {mock_achievement_based_name: mock_dependent_badge.id}


@pytest.fixture
def rule_dependency_service(
    rule_factory, event_configuration_factory, event_factory, mock_action_event_based_dict, mock_filters_dict
):
    def _setup(rule=None, created_at=None, dependencies=None):
        event_configuration = event_configuration_factory(event_type__name=mock_event_based_name)
        current_event = event_factory(configuration=event_configuration)
        rule = rule or rule_factory(
            event_configuration=event_configuration,
            action=mock_action_event_based_dict,
            filters=mock_filters_dict
        )
        return RuleDependencyService(rule, created_at or now(), current_event, dependencies or {})

    return _setup
