import pytest


@pytest.fixture
def avatar_with_rule(avatar_factory, rule_distribution_with_points):
    """
    Create an avatar with a single points distribution rule.
    """

    def _create(stage=1, points=50, **avatar_kwargs):
        avatar = avatar_factory(stage=stage, **avatar_kwargs)
        rule = rule_distribution_with_points(points=points)
        avatar.rules.set([rule])
        return avatar

    return _create


@pytest.fixture
def avatar_without_rules(avatar_factory):
    """
    Create an avatar without any rules attached.
    """

    def _create(stage=1, **avatar_kwargs):
        return avatar_factory(stage=stage, **avatar_kwargs)

    return _create
