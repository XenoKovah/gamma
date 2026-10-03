"""
The Subtitle Superhero badge's board is ranked by subtitle lines contributed, not points.
"""
import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient

from achievements.tests.factories import AchievementFactory
from badges.factories import BadgeFactory
from badges.models import Badge
from leaderboard import subtitle_ranking
from users.factories import GammaUserFactory

pytestmark = pytest.mark.django_db


def award(user, badge) -> None:
    AchievementFactory(
        user=user,
        content_type=ContentType.objects.get_for_model(Badge),
        object_id=badge.id,
    )


@pytest.fixture
def lines(monkeypatch):
    mapping = {"few_lines": 10, "many_lines": 500, "mid_lines": 100}
    monkeypatch.setattr(subtitle_ranking, "get_subtitle_lines", lambda: mapping)
    monkeypatch.setattr("leaderboard.api.v0.views.get_subtitle_lines", lambda: mapping)
    return mapping


def test_subtitle_superhero_board_is_ordered_by_lines(auth_client: APIClient, lines) -> None:
    badge = BadgeFactory(title="Subtitle Superhero")
    assert badge.slug == "subtitle-superhero"
    for uid, points in (("few_lines", 900), ("many_lines", 100), ("mid_lines", 500), ("no_file_entry", 999)):
        award(GammaUserFactory(user_uid=uid, points=points), badge)

    data = auth_client.get(
        "/api/v0/leaderboard/badge/subtitle-superhero?username=many_lines&signup_source=main"
    ).json()

    assert [m["user_uid"] for m in data["top10"]] == ["many_lines", "mid_lines", "few_lines", "no_file_entry"]
    assert data["rank"] == 1
    assert [m["points"] for m in data["top10"]] == [500, 100, 10, 0]
    assert data["badge"]["score_label"] == "Subtitle Lines Changed"


def test_other_badges_still_rank_by_points(auth_client: APIClient, lines) -> None:
    badge = BadgeFactory(title="Some Other Badge")
    for uid, points in (("few_lines", 900), ("many_lines", 100)):
        award(GammaUserFactory(user_uid=uid, points=points), badge)

    data = auth_client.get(f"/api/v0/leaderboard/badge/{badge.slug}?username=x&signup_source=main").json()

    assert [m["user_uid"] for m in data["top10"]] == ["few_lines", "many_lines"]
    assert [m["points"] for m in data["top10"]] == [900, 100]
    assert data["badge"]["score_label"] is None
