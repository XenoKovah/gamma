import pytest


@pytest.fixture
def user_avatar_config_with_set(user_avatar_config_factory, gamma_user_factory, avatar_set_factory):
    """
    Create a user avatar config with an avatar set.
    """

    def _create(user_points=100, stages=3, points_per_stage=50, user=None, **user_kwargs):
        if user is None:
            user = gamma_user_factory(points=user_points, **user_kwargs)
        avatars = [avatar_set_factory() for _ in range(stages)]
        avatar_set = avatar_set_factory(is_draft=False, avatars=avatars)
        return user_avatar_config_factory(user=user, avatar_set=avatar_set)

    return _create


@pytest.fixture
def user_avatar_config_with_stages(user_avatar_config_factory, gamma_user_factory, avatar_set_with_staged_avatars):
    """
    Create a user avatar config with staged avatars.
    """

    def _create(user_points=100, stages=3, points_per_stage=50, user=None, **user_kwargs):
        if user is None:
            user = gamma_user_factory(points=user_points, **user_kwargs)
        avatar_set = avatar_set_with_staged_avatars(stages=stages, points_per_stage=points_per_stage)
        return user_avatar_config_factory(user=user, avatar_set=avatar_set)

    return _create


@pytest.fixture
def user_avatar_config_without_avatar_set(user_avatar_config_factory, gamma_user_factory):
    """
    Create a user avatar config without an avatar set.
    """

    def _create(user_points=100, **user_kwargs):
        user = gamma_user_factory(points=user_points, **user_kwargs)
        return user_avatar_config_factory(user=user, avatar_set=None)

    return _create


@pytest.fixture
def user_avatar_config_with_empty_avatar_set(
    user_avatar_config_factory,
    gamma_user_factory,
    avatar_set_without_avatars,
):
    """
    Create a user avatar config with an empty avatar set.
    """

    def _create(user_points=100, **user_kwargs):
        user = gamma_user_factory(points=user_points, **user_kwargs)
        avatar_set = avatar_set_without_avatars()
        return user_avatar_config_factory(user=user, avatar_set=avatar_set)

    return _create
