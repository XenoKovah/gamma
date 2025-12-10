from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from events.enums import RggInternalEventTypes
from events.models import EventConfiguration

if TYPE_CHECKING:
    from rules.tests.factories import RuleFactory


@pytest.fixture
def rule_distribution_with_points(rule_factory: RuleFactory) -> RuleFactory:
    """
    Create a rule with specific points distribution action.
    """

    def _create(points=50):
        event_configuration = EventConfiguration.objects.get(
            event_type__name=RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value
        )
        return rule_factory(
            event_configuration=event_configuration,
            action={RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value: {"points": points}},
            filters={},
        )

    return _create
