"""
The instructor-free view of each leaderboard (``hide_instructors=1``).

Instructors out-score everyone because writing class material pays the most points, so
every board offers a second view with them removed. What these tests pin down is that
it is genuinely a *different board* rather than the same one with rows blanked out: the
list refills from the learners who were pushed off the bottom, and every rank closes up.
"""
from typing import List

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from rest_framework.test import APIClient

from achievements.tests.factories import AchievementFactory
from badges.factories import BadgeFactory
from badges.models import Badge
from leaderboard.instructors import get_instructor_user_uids, is_instructor_badge_slug
from users.factories import GammaUserFactory

pytestmark = pytest.mark.django_db


def award(user, badge) -> None:
    """
    Mark ``badge`` as earned by ``user``.

    A rule-less achievement counts as completed (``all([])`` is ``True``), which is
    exactly how a manually granted badge — every instructor badge — is stored.
    """
    AchievementFactory(
        user=user,
        content_type=ContentType.objects.get_for_model(Badge),
        object_id=badge.id,
    )


def uids(members: List[dict]) -> List[str]:
    """
    Provide the user_uids of a list of serialized leaderboard members.
    """
    return [member["user_uid"] for member in members]


class TestInstructorIdentification:
    """
    Which badges — and so which learners — count as instructors.
    """

    @pytest.mark.parametrize(
        "slug",
        ["instructor", "6h-instructor", "16h-instructor", "154h-instructor"],
    )
    def test_instructor_slugs_are_recognized(self, slug: str) -> None:
        assert is_instructor_badge_slug(slug)

    @pytest.mark.parametrize(
        "slug",
        [
            None,
            "",
            "instructor-of-the-year",  # the word has to end the slug
            "constructor",  # ends in the same letters without the separator
            "reverse-engineer",
        ],
    )
    def test_other_slugs_are_not(self, slug: str) -> None:
        assert not is_instructor_badge_slug(slug)

    def test_collects_holders_of_every_instructor_badge(self) -> None:
        flat = BadgeFactory(title="Instructor")
        scaled = BadgeFactory(title="Instructor 16h")
        scaled.slug = "16h-instructor"
        scaled.save()
        unrelated = BadgeFactory(title="Firmware Master")

        flat_holder = GammaUserFactory(user_uid="flat_holder", points=100)
        scaled_holder = GammaUserFactory(user_uid="scaled_holder", points=200)
        learner = GammaUserFactory(user_uid="learner", points=300)
        award(flat_holder, flat)
        award(scaled_holder, scaled)
        award(learner, unrelated)

        assert get_instructor_user_uids() == {"flat_holder", "scaled_holder"}

    def test_a_deactivated_instructor_badge_still_marks_its_holder(self) -> None:
        """
        Deactivating a badge hides it but leaves the points it paid, so its holder is
        still sitting at the top of the board and still has to be filterable.
        """
        badge = BadgeFactory(title="Instructor", is_active=False)
        holder = GammaUserFactory(user_uid="hidden_badge_holder", points=100)
        award(holder, badge)

        assert get_instructor_user_uids() == {"hidden_badge_holder"}


class TestPersonalizedLeaderboardHidesInstructors:
    """
    The main (and per-course) board, which is ranked in Redis.
    """

    @pytest.fixture
    def board(self):
        """
        Build a board of 5 learners and 2 instructors with distinct point totals.

        Points descend in the order created, so the full board reads
        i_900, l_800, i_700, l_600, l_500, l_400, l_300 and the instructor-free one
        reads l_800, l_600, l_500, l_400, l_300.
        """
        instructor_badge = BadgeFactory(title="Instructor")
        for uid, points, is_instructor in [
            ("i_900", 900, True),
            ("l_800", 800, False),
            ("i_700", 700, True),
            ("l_600", 600, False),
            ("l_500", 500, False),
            ("l_400", 400, False),
            ("l_300", 300, False),
        ]:
            user = GammaUserFactory(user_uid=uid, signup_source="main", points=points)
            if is_instructor:
                award(user, instructor_badge)
        call_command("initialize_leaderboard")

    def _get(self, client: APIClient, username: str, hide: bool = False) -> dict:
        endpoint = f"/api/v0/leaderboard?username={username}&signup_source=main"
        if hide:
            endpoint += "&hide_instructors=1"
        response = client.get(endpoint)
        assert response.status_code == 200
        return response.json()

    def test_default_board_is_unchanged(self, auth_client: APIClient, board) -> None:
        data = self._get(auth_client, "l_600")

        assert uids(data["top10"]) == ["i_900", "l_800", "i_700", "l_600", "l_500", "l_400", "l_300"]
        assert data["rank"] == 4
        assert data["viewer_hidden"] is False

    def test_instructors_are_dropped_and_ranks_close_up(self, auth_client: APIClient, board) -> None:
        data = self._get(auth_client, "l_600", hide=True)

        assert uids(data["top10"]) == ["l_800", "l_600", "l_500", "l_400", "l_300"]
        # 4th of everyone, but 2nd once the two instructors above are gone.
        assert data["rank"] == 2
        assert data["viewer_hidden"] is False

    def test_learners_pushed_off_the_bottom_are_pulled_back_on(
        self, auth_client: APIClient, board, mocker,
    ) -> None:
        """
        The point of refilling: with a top list of 3, hiding the two instructors must not
        leave a list of one — it has to reach further down the board for the learners the
        instructors were keeping off it.
        """
        mocker.patch("leaderboard.usecases.GetPersonalizedLeaderboardUseCase.TOP_MEMBERS_LIMIT", 3)

        assert uids(self._get(auth_client, "l_300")["top10"]) == ["i_900", "l_800", "i_700"]
        assert uids(self._get(auth_client, "l_300", hide=True)["top10"]) == ["l_800", "l_600", "l_500"]

    def test_competitor_window_skips_instructors(self, auth_client: APIClient, board, mocker) -> None:
        """
        A learner below the top list gets a window of their nearest competitors; on the
        instructor-free board those neighbours must be learners, not the instructors who
        happen to sit next to them.
        """
        mocker.patch("leaderboard.usecases.GetPersonalizedLeaderboardUseCase.TOP_MEMBERS_LIMIT", 1)

        data = self._get(auth_client, "l_500", hide=True)

        assert uids(data["top10"]) == ["l_800"]
        assert "i_900" not in uids(data["competitors"])
        assert "i_700" not in uids(data["competitors"])
        assert "l_500" in uids(data["competitors"])

    def test_an_instructor_viewing_the_filtered_board_is_not_ranked_on_it(
        self, auth_client: APIClient, board,
    ) -> None:
        """
        An instructor is not on the instructor-free board, so they get no rank and no
        competitors — and ``viewer_hidden`` tells the dashboard to skip the "you are not
        ranked yet" row it would otherwise add for an unranked viewer.
        """
        data = self._get(auth_client, "i_900", hide=True)

        assert uids(data["top10"]) == ["l_800", "l_600", "l_500", "l_400", "l_300"]
        assert data["rank"] is None
        assert data["competitors"] == []
        assert data["viewer_hidden"] is True


class TestBadgeLeaderboardHidesInstructors:
    """
    The per-badge board, ranked in Python over the badge's earners.
    """

    def test_instructors_are_dropped_and_ranks_close_up(self, auth_client: APIClient) -> None:
        badge = BadgeFactory(title="Firmware Master")
        instructor_badge = BadgeFactory(title="Instructor")
        instructor = GammaUserFactory(user_uid="instructor", points=900)
        learner = GammaUserFactory(user_uid="learner", points=100)
        award(instructor, instructor_badge)
        award(instructor, badge)
        award(learner, badge)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=learner&signup_source=main"

        default = auth_client.get(endpoint).json()
        assert uids(default["top10"]) == ["instructor", "learner"]
        assert default["rank"] == 2
        assert default["badge"]["is_instructor_badge"] is False

        hidden = auth_client.get(f"{endpoint}&hide_instructors=1").json()
        assert uids(hidden["top10"]) == ["learner"]
        assert hidden["rank"] == 1

    def test_in_progress_section_is_filtered_too(self, auth_client: APIClient) -> None:
        from achievements.tests.factories import AchievementRuleFactory
        from achievements.models import AchievementRule

        badge = BadgeFactory(title="Firmware Master")
        instructor_badge = BadgeFactory(title="Instructor")
        instructor = GammaUserFactory(user_uid="instructor", points=900)
        award(instructor, instructor_badge)

        achievement = AchievementFactory(
            user=instructor,
            content_type=ContentType.objects.get_for_model(Badge),
            object_id=badge.id,
        )
        AchievementRuleFactory(
            achievement=achievement,
            status=AchievementRule.Statuses.ACTIVE,
            dependencies={"is_achieved": False, "events": {"points": {"count": 5, "goal": 10}}},
        )

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=learner&signup_source=main"

        assert uids(auth_client.get(endpoint).json()["in_progress"]) == ["instructor"]
        assert auth_client.get(f"{endpoint}&hide_instructors=1").json()["in_progress"] == []

    def test_an_instructor_badges_own_board_is_never_filtered(self, auth_client: APIClient) -> None:
        """
        Hiding instructors on an instructor badge's own board would empty the page, so the
        request is served unfiltered and the response says so, letting the dashboard drop
        the toggle rather than honour a sticky preference into a blank list.
        """
        instructor_badge = BadgeFactory(title="Instructor")
        instructor = GammaUserFactory(user_uid="instructor", points=900)
        award(instructor, instructor_badge)

        endpoint = (
            f"/api/v0/leaderboard/badge/{instructor_badge.slug}"
            "?username=learner&signup_source=main&hide_instructors=1"
        )
        data = auth_client.get(endpoint).json()

        assert data["badge"]["is_instructor_badge"] is True
        assert uids(data["top10"]) == ["instructor"]


class TestUsersLeaderboardHidesInstructors:
    """
    The explicit-user-set board behind the per-country page and the per-course
    "Completed" section.
    """

    ENDPOINT = "/api/v0/leaderboard/users"

    def test_instructors_are_dropped_and_ranks_close_up(self, auth_client: APIClient) -> None:
        instructor_badge = BadgeFactory(title="Instructor")
        instructor = GammaUserFactory(user_uid="instructor", signup_source="main", points=900)
        GammaUserFactory(user_uid="learner", signup_source="main", points=100)
        award(instructor, instructor_badge)

        payload = {
            "username": "learner",
            "signup_source": "main",
            "user_uids": ["instructor", "learner"],
        }

        default = auth_client.post(self.ENDPOINT, payload, format="json").json()
        assert uids(default["top10"]) == ["instructor", "learner"]
        assert default["rank"] == 2

        hidden = auth_client.post(
            self.ENDPOINT, {**payload, "hide_instructors": True}, format="json"
        ).json()
        assert uids(hidden["top10"]) == ["learner"]
        assert hidden["rank"] == 1
        assert hidden["viewer_hidden"] is False


class TestInstructorUserUidsView:
    """
    The uid list the dashboard needs for the one section it ranks itself.
    """

    ENDPOINT = "/api/v0/leaderboard/instructor-uids"

    def test_lists_instructors(self, auth_client: APIClient) -> None:
        instructor_badge = BadgeFactory(title="Instructor")
        instructor = GammaUserFactory(user_uid="instructor", points=900)
        GammaUserFactory(user_uid="learner", points=100)
        award(instructor, instructor_badge)

        response = auth_client.get(self.ENDPOINT)

        assert response.status_code == 200
        assert response.json() == {"user_uids": ["instructor"]}

    def test_is_forbidden_for_unauthorized_user(self, client: APIClient) -> None:
        assert client.get(self.ENDPOINT).status_code == 403
