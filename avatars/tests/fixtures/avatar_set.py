import pytest


@pytest.fixture
def avatar_set_with_staged_avatars(avatar_set_factory, avatar_with_rule):
    """
    Create an avatar set with multiple staged avatars, each with rules.
    """

    def _create(stages=3, points_per_stage=50, is_draft=False, **set_kwargs):
        avatars = [avatar_with_rule(stage=i, points=i * points_per_stage) for i in range(1, stages + 1)]
        avatar_set = avatar_set_factory(is_draft=is_draft, avatars=[], **set_kwargs)
        avatar_set.avatars.set(avatars)
        return avatar_set

    return _create


@pytest.fixture
def avatar_set_without_avatars(avatar_set_factory):
    """
    Create an empty avatar set with no avatars.
    """

    def _create(is_draft=False, **set_kwargs):
        return avatar_set_factory(is_draft=is_draft, avatars=[], **set_kwargs)

    return _create
