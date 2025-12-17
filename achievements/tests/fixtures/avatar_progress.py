import pytest
from achievements.services.progress import get_avatar_progress_service


@pytest.fixture
def avatar_progress_service(user_avatar_config_with_stages):
    """
    Create an AvatarProgressService instance with a configured user.
    """

    def _create(user_points=100, stages=3, points_per_stage=50, **kwargs):
        config = user_avatar_config_with_stages(
            user_points=user_points,
            stages=stages,
            points_per_stage=points_per_stage,
            **kwargs,
        )
        return get_avatar_progress_service(username=config.user.user_uid, config=config)

    return _create


@pytest.fixture
def avatar_progress_service_without_avatar_set(user_avatar_config_without_avatar_set):
    """
    Create an AvatarProgressService with no avatar set.
    """

    def _create(user_points=100, **kwargs):
        config = user_avatar_config_without_avatar_set(user_points=user_points, **kwargs)
        return get_avatar_progress_service(username=config.user.user_uid, config=config)

    return _create


@pytest.fixture
def avatar_progress_service_with_empty_set(user_avatar_config_with_empty_avatar_set):
    """
    Create an AvatarProgressService with an empty avatar set.
    """

    def _create(user_points=100, **kwargs):
        config = user_avatar_config_with_empty_avatar_set(user_points=user_points, **kwargs)
        return get_avatar_progress_service(username=config.user.user_uid, config=config)

    return _create


@pytest.fixture
def avatar_progress_service_with_completed_stages(user_with_completed_avatar_stages):
    """
    Create an AvatarProgressService for a user with completed stages.
    """

    def _create(user_points=100, stages=3, points_per_stage=50, completed_stages=1):
        config = user_with_completed_avatar_stages(
            user_points=user_points,
            stages=stages,
            points_per_stage=points_per_stage,
            completed_stages=completed_stages,
        )
        return get_avatar_progress_service(username=config.user.user_uid, config=config)

    return _create
