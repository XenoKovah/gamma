"""
Tests for AvatarProgressService.
"""

import pytest

from achievements.services.progress import AvatarProgressService, get_avatar_progress_service


@pytest.mark.django_db
class TestAvatarProgressServiceInit:
    """
    Tests for AvatarProgressService initialization.
    """

    def test_init_handles_missing_avatar_set(self, user_avatar_config_without_avatar_set):
        config = user_avatar_config_without_avatar_set()

        service = get_avatar_progress_service(config)

        assert service.avatar_set is None


@pytest.mark.django_db
class TestCalculateProgress:
    """
    Tests for calculate_progress.
    """

    def test_returns_current_points_from_user(self, avatar_progress_service):
        service = avatar_progress_service(user_points=150)

        result = service.calculate_progress()

        assert result["current_points"] == 150

    def test_returns_zero_points_when_user_has_none(self, avatar_progress_service):
        service = avatar_progress_service(user_points=0)

        result = service.calculate_progress()

        assert result["current_points"] == 0

    def test_returns_next_avatar_when_no_progress(self, avatar_progress_service):
        service = avatar_progress_service(stages=3, points_per_stage=50)

        result = service.calculate_progress()

        assert result["next_avatar"] is not None

    def test_returns_none_current_avatar_when_no_progress(self, avatar_progress_service):
        service = avatar_progress_service(stages=3, points_per_stage=50)

        result = service.calculate_progress()

        assert result["current_avatar"] is None


@pytest.mark.django_db
class TestResolveCurrent:
    """
    Tests for resolve_current method.
    """

    def test_returns_none_when_no_avatar_set(self, avatar_progress_service_without_avatar_set):
        service = avatar_progress_service_without_avatar_set()

        result = service.resolve_current()

        assert result is None

    def test_returns_none_when_no_completed_avatars(self, avatar_progress_service):
        service = avatar_progress_service(stages=3)

        result = service.resolve_current()

        assert result is None

    def test_returns_completed_avatar(self, avatar_progress_service_with_completed_stages):
        service = avatar_progress_service_with_completed_stages(
            stages=3,
            points_per_stage=50,
            completed_stages=1,
        )

        result = service.resolve_current()

        assert result is not None
        assert result.stage == 1


@pytest.mark.django_db
class TestResolveNext:
    """
    Tests for resolve_next method.
    """

    def test_returns_first_avatar_when_no_current(self, avatar_progress_service):
        service = avatar_progress_service(stages=3)

        result = service.resolve_next()

        assert result is not None
        assert result.stage == 1

    def test_returns_none_when_no_avatar_set(self, avatar_progress_service_without_avatar_set):
        service = avatar_progress_service_without_avatar_set()

        result = service.resolve_next()

        assert result is None

    def test_returns_none_when_empty_avatar_set(self, avatar_progress_service_with_empty_set):
        service = avatar_progress_service_with_empty_set()

        result = service.resolve_next()

        assert result is None

    def test_returns_next_stage_after_current(self, avatar_progress_service_with_completed_stages):
        service = avatar_progress_service_with_completed_stages(stages=3, points_per_stage=50, completed_stages=1)

        result = service.resolve_next()

        assert result is not None
        assert result.stage == 2

    def test_returns_none_when_all_stages_completed(self, avatar_progress_service_with_completed_stages):
        service = avatar_progress_service_with_completed_stages(stages=3, points_per_stage=50, completed_stages=3)

        result = service.resolve_next()

        assert result is None


@pytest.mark.django_db
class TestGetRequiredPointsForAvatar:
    """
    Tests for _get_required_points_for_avatar static method.
    """

    def test_returns_zero_when_avatar_is_none(self):
        result = AvatarProgressService._get_required_points_for_avatar(None)

        assert result == 0

    def test_returns_zero_when_avatar_has_no_rules(self, avatar_without_rules):
        avatar = avatar_without_rules()

        result = AvatarProgressService._get_required_points_for_avatar(avatar)

        assert result == 0

    def test_returns_points_from_rule_action(self, avatar_with_rule):
        avatar = avatar_with_rule(points=100)

        result = AvatarProgressService._get_required_points_for_avatar(avatar)

        assert result == 100

    def test_sums_points_from_multiple_rules(self, avatar_factory, rule_distribution_with_points):
        avatar = avatar_factory()
        rule1 = rule_distribution_with_points(points=50)
        rule2 = rule_distribution_with_points(points=75)
        avatar.rules.set([rule1, rule2])

        result = AvatarProgressService._get_required_points_for_avatar(avatar)

        assert result == 125
