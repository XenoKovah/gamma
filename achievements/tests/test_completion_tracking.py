import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from achievements.usecases import AchievementCompletionUseCase
from badges.models import Badge


@pytest.fixture
def badge_achievement(achievement_factory, badge_factory, gamma_user_factory):
    """
    An in-progress badge achievement (no completion timestamp yet).
    """
    badge = badge_factory()
    return achievement_factory(
        user=gamma_user_factory(),
        content_type=ContentType.objects.get_for_model(Badge),
        object_id=badge.id,
    )


@pytest.mark.django_db
def test_mark_completed_stamps_once(badge_achievement):
    assert badge_achievement.completed_at is None

    assert badge_achievement.mark_completed() is True
    first_completed_at = badge_achievement.completed_at
    assert first_completed_at is not None

    # A later completion event against the same achievement must not move the timestamp.
    assert badge_achievement.mark_completed() is False
    badge_achievement.refresh_from_db()
    assert badge_achievement.completed_at == first_completed_at


@pytest.mark.django_db
def test_completion_usecase_stamps_completed_at(badge_achievement):
    AchievementCompletionUseCase().execute(badge_achievement)

    badge_achievement.refresh_from_db()
    assert badge_achievement.completed_at is not None
    # The notification has not been shown yet.
    assert badge_achievement.notification_seen_at is None


@pytest.mark.django_db
def test_completion_usecase_fires_obtained_event_only_once(badge_achievement):
    """
    Re-running completion for an already-complete achievement (a shared rule can
    keep routing events at it) must not emit another internal obtained event.
    """
    from events.enums import RggInternalEventTypes
    from events.models import Event

    AchievementCompletionUseCase().execute(badge_achievement)
    AchievementCompletionUseCase().execute(badge_achievement)

    obtained_events = Event.objects.filter(
        username=badge_achievement.user.user_uid,
        configuration__event_type__name=RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value,
    )
    assert obtained_events.count() == 1


@pytest.mark.django_db
def test_manual_award_stamps_completed_at(badge_factory, gamma_user_factory):
    badge = badge_factory()
    user = gamma_user_factory()

    assert badge.award_to_user(user) is True

    achievement = user.achievement_set.get(
        content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id
    )
    assert achievement.completed_at is not None
    assert achievement.notification_seen_at is None

    # Re-awarding is a no-op and must not reset the original completion moment.
    first_completed_at = achievement.completed_at
    assert badge.award_to_user(user) is False
    achievement.refresh_from_db()
    assert achievement.completed_at == first_completed_at


@pytest.mark.django_db
def test_completion_usecase_pays_badge_points_once(achievement_factory, badge_factory, gamma_user_factory):
    """
    The first rule-driven completion grants the badge's completion points
    ("Points for completion" on the dashboard); re-completions (a shared rule
    can keep routing events at the achievement) must not pay again.
    """
    badge = badge_factory(points=150)
    user = gamma_user_factory()
    starting_points = user.points
    achievement = achievement_factory(
        user=user,
        content_type=ContentType.objects.get_for_model(Badge),
        object_id=badge.id,
    )

    AchievementCompletionUseCase().execute(achievement)
    user.refresh_from_db()
    assert user.points == starting_points + 150

    AchievementCompletionUseCase().execute(achievement)
    user.refresh_from_db()
    assert user.points == starting_points + 150


@pytest.mark.django_db
def test_completion_usecase_without_badge_points_pays_nothing(badge_achievement):
    starting_points = badge_achievement.user.points

    AchievementCompletionUseCase().execute(badge_achievement)

    badge_achievement.user.refresh_from_db()
    assert badge_achievement.user.points == starting_points
