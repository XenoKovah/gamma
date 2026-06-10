import urllib.parse
from typing import Type
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from pytest_mock.plugin import MockerFixture
from rest_framework.test import APIClient

from achievements.tests.factories import AchievementFactory, AchievementRuleFactory
from achievements.models import AchievementRule
from badges.factories import BadgeFactory
from badges.models import Badge
from leaderboard.api.v0.views import BadgeLeaderBoardView, LeaderBoardView, UsersLeaderBoardView
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.factories import LeaderboardRetrievingContextFactory
from users.factories import GammaUserCoursePointsFactory, GammaUserFactory
from users.models import GammaUser


pytestmark = pytest.mark.django_db


class TestLeaderBoardView:
    @pytest.mark.django_db
    @patch("leaderboard.api.v0.views.LeaderBoardView._collect_response_data", Mock(return_value={}))
    def test_get_request_creates_requested_user_if_he_does_not_exist(self, auth_client: APIClient) -> None:
        user_uid = "test_edx_user"
        endpoint = f"/api/v0/leaderboard?username={user_uid}&signup_source=main"

        assert not GammaUser.objects.filter(user_uid=user_uid).exists()

        auth_client.get(endpoint)

        assert GammaUser.objects.filter(user_uid=user_uid).exists()

    @pytest.mark.django_db
    def test_get_request_provide_collect_response_data_result_in_response_body(
        self,
        auth_client: APIClient,
        mocker: MockerFixture,
    ) -> None:
        user_uid = "test_edx_user"
        user_signup_source = "RG"
        course_id = "course-v1:OpenedX+DemoX+DemoCourse"
        quoted_course_id = urllib.parse.quote(course_id)
        endpoint = (
            f"/api/v0/leaderboard?username={user_uid}&signup_source={user_signup_source}&course_id={quoted_course_id}"
        )
        leaderboard_retrieving_context = LeaderboardRetrievingContext(user_uid, user_signup_source, course_id)
        collect_response_data_result = {
            "top10": [
                {
                    "user_uid": "user_uid_1",
                    "signup_source": "RG",
                    "badges": [],
                    "points": 85,
                },
                {
                    "user_uid": "test_edx_user",
                    "signup_source": "RG",
                    "badges": [],
                    "points": 75,
                },
                {
                    "user_uid": "user_uid_2",
                    "signup_source": "RG",
                    "badges": [],
                    "points": 15,
                },
            ],
            "rank": 2,
            "user_uid": "test_edx_user",
            "competitors": [],
        }
        collect_response_data_mock = mocker.patch(
            "leaderboard.api.v0.views.LeaderBoardView._collect_response_data",
            Mock(return_value=collect_response_data_result),
        )

        response = auth_client.get(endpoint)

        collect_response_data_mock.assert_called_once_with(leaderboard_retrieving_context)
        assert response.status_code == 200
        assert response.json() == collect_response_data_result

    def test_making_get_request_is_forbidden_for_unauthorized_user(self, client: APIClient) -> None:
        user_uid = "test_edx_user"
        endpoint = f"/api/v0/leaderboard?username={user_uid}&signup_source=main"

        response = client.get(endpoint)

        assert response.status_code == 403

    @patch("leaderboard.api.v0.views.ORMLeaderboardMemberDataRepository")
    @patch("leaderboard.api.v0.views.RedisLeaderboardRepository")
    def test_collect_response_data_use_get_personalized_leaderboard_use_case_for_response_data_building(
        self,
        redis_leaderboard_repository_mock: MagicMock,
        orm_leaderboard_member_data_repository_mock: MagicMock,
        leaderboard_retrieving_context_factory: Type[LeaderboardRetrievingContextFactory],
        mocker: MockerFixture,
    ) -> None:
        user_uid = "test_edx_user"
        leaderboard_retrieving_context = leaderboard_retrieving_context_factory(user_uid=user_uid)
        leaders_mock = [
            {
                "user_uid": "user_uid_1",
                "signup_source": "RG",
                "badges": [],
                "points": 85,
            },
            {
                "user_uid": "test_edx_user",
                "signup_source": "RG",
                "badges": [],
                "points": 75,
            },
            {
                "user_uid": "user_uid_2",
                "signup_source": "RG",
                "badges": [],
                "points": 15,
            },
        ]
        competitors_mock = []
        rank_mock = 2
        expected_response_data = {
            "top10": leaders_mock,
            "rank": rank_mock,
            "user_uid": leaderboard_retrieving_context.user_uid,
            "competitors": competitors_mock,
        }
        use_case_mock = mocker.patch(
            "leaderboard.api.v0.views.GetPersonalizedLeaderboardUseCase",
            Mock(return_value=Mock(execute=Mock(return_value=(leaders_mock, competitors_mock, rank_mock)))),
        )

        actual_response_data = LeaderBoardView()._collect_response_data(leaderboard_retrieving_context)

        redis_leaderboard_repository_mock.assert_called_once_with()
        orm_leaderboard_member_data_repository_mock.assert_called_once_with()
        use_case_mock.assert_called_once_with(
            redis_leaderboard_repository_mock.return_value,
            orm_leaderboard_member_data_repository_mock.return_value,
        )
        use_case_mock.return_value.execute.assert_called_once_with(leaderboard_retrieving_context)
        assert actual_response_data == expected_response_data


class TestBadgeLeaderBoardView:
    """
    Test Case for the BadgeLeaderBoardView (per-badge filtered leaderboard).
    """

    @staticmethod
    def _award_badge(user, badge):
        """
        Mark ``badge`` as earned by ``user`` (an achievement with no rules counts
        as completed, mirroring ``Achievement.all_rules_completed``).
        """
        AchievementFactory(
            user=user,
            content_type=ContentType.objects.get_for_model(Badge),
            object_id=badge.id,
        )

    def test_making_get_request_is_forbidden_for_unauthorized_user(self, client: APIClient) -> None:
        response = client.get("/api/v0/leaderboard/badge/some-badge?username=test_edx_user&signup_source=main")

        assert response.status_code == 403

    def test_unknown_badge_returns_404(self, auth_client: APIClient) -> None:
        endpoint = "/api/v0/leaderboard/badge/does-not-exist?username=test_edx_user&signup_source=main"

        response = auth_client.get(endpoint)

        assert response.status_code == 404
        assert response.json() == {"error": "Badge not found."}

    def test_returns_badge_earners_ranked_by_points(self, auth_client: APIClient) -> None:
        badge = BadgeFactory(title="Firmware Master Level 1", description="Complete Arch4001")
        low = GammaUserFactory(user_uid="low_points_user", points=10)
        high = GammaUserFactory(user_uid="high_points_user", points=90)
        self._award_badge(low, badge)
        self._award_badge(high, badge)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=high_points_user&signup_source=main"
        response = auth_client.get(endpoint)

        assert response.status_code == 200
        data = response.json()
        assert data["badge"]["slug"] == badge.slug
        assert data["badge"]["title"] == "Firmware Master Level 1"
        assert data["badge"]["description"] == "Complete Arch4001"
        assert data["competitors"] == []
        # Earners are ranked by points, highest first.
        assert [member["user_uid"] for member in data["top10"]] == ["high_points_user", "low_points_user"]
        assert [member["points"] for member in data["top10"]] == [90, 10]
        # The requesting user earned the badge and tops the list.
        assert data["rank"] == 1

    def test_rank_is_none_when_requesting_user_has_not_earned_badge(self, auth_client: APIClient) -> None:
        badge = BadgeFactory()
        earner = GammaUserFactory(user_uid="earner", points=50)
        self._award_badge(earner, badge)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=non_earner&signup_source=main"
        response = auth_client.get(endpoint)

        assert response.status_code == 200
        data = response.json()
        assert [member["user_uid"] for member in data["top10"]] == ["earner"]
        assert data["rank"] is None

    def test_only_badge_earners_are_returned(self, auth_client: APIClient) -> None:
        badge = BadgeFactory()
        other_badge = BadgeFactory()
        earner = GammaUserFactory(user_uid="earner", points=50)
        non_earner = GammaUserFactory(user_uid="other_badge_holder", points=100)
        self._award_badge(earner, badge)
        self._award_badge(non_earner, other_badge)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=earner&signup_source=main"
        response = auth_client.get(endpoint)

        assert response.status_code == 200
        data = response.json()
        assert [member["user_uid"] for member in data["top10"]] == ["earner"]

    def test_members_are_limited_to_the_top_100(self, auth_client: APIClient, mocker: MockerFixture) -> None:
        mocker.patch.object(BadgeLeaderBoardView, "MEMBERS_LIMIT", 2)
        badge = BadgeFactory()
        for index in range(3):
            user = GammaUserFactory(user_uid=f"earner_{index}", points=index)
            self._award_badge(user, badge)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=earner_2&signup_source=main"
        response = auth_client.get(endpoint)

        assert response.status_code == 200
        data = response.json()
        # Only the top 2 earners are serialized, but the rank reflects all earners.
        assert [member["user_uid"] for member in data["top10"]] == ["earner_2", "earner_1"]
        assert data["rank"] == 1

    @staticmethod
    def _add_progress(user, badge, badge_ct, goal, count):
        """
        Give ``user`` an in-progress (incomplete) achievement for ``badge``.
        """
        achievement = AchievementFactory(user=user, content_type=badge_ct, object_id=badge.id)
        AchievementRuleFactory(
            achievement=achievement,
            status=AchievementRule.Statuses.ACTIVE,
            dependencies={"is_achieved": False, "events": {"points": {"goal": goal, "count": count}}},
        )

    def test_in_progress_users_are_listed_separately_and_ranked_by_percent(self, auth_client: APIClient) -> None:
        badge = BadgeFactory()
        badge_ct = ContentType.objects.get_for_model(Badge)

        # An earner stays in the completed list.
        earner = GammaUserFactory(user_uid="earner", points=2000)
        self._award_badge(earner, badge)

        # Two users progressing toward a 1000-point goal (10% and 70%).
        low = GammaUserFactory(user_uid="ip_low", points=100)
        high = GammaUserFactory(user_uid="ip_high", points=700)
        self._add_progress(low, badge, badge_ct, goal=1000, count=100)
        self._add_progress(high, badge, badge_ct, goal=1000, count=700)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=ip_high&signup_source=main"
        response = auth_client.get(endpoint)

        assert response.status_code == 200
        data = response.json()
        # Earner only in top10; in-progress users are a separate, percent-ranked list.
        assert [member["user_uid"] for member in data["top10"]] == ["earner"]
        assert [member["user_uid"] for member in data["in_progress"]] == ["ip_high", "ip_low"]
        assert [member["progress_percent"] for member in data["in_progress"]] == [70, 10]
        # The requesting user (ip_high) leads the in-progress list.
        assert data["in_progress_rank"] == 1

    def test_progress_percent_is_floored_to_match_dashboard(self, auth_client: APIClient) -> None:
        # 35 / 1000 = 3.5% must floor to 3 (matching the dashboard's calculateBadgeProgress),
        # not round up to 4.
        badge = BadgeFactory()
        badge_ct = ContentType.objects.get_for_model(Badge)
        user = GammaUserFactory(user_uid="halfway", points=35)
        self._add_progress(user, badge, badge_ct, goal=1000, count=35)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=halfway&signup_source=main"
        response = auth_client.get(endpoint)

        assert response.status_code == 200
        assert response.json()["in_progress"][0]["progress_percent"] == 3

    def test_zero_progress_users_are_excluded_from_in_progress(self, auth_client: APIClient) -> None:
        badge = BadgeFactory()
        badge_ct = ContentType.objects.get_for_model(Badge)
        user = GammaUserFactory(user_uid="no_progress", points=0)
        self._add_progress(user, badge, badge_ct, goal=1000, count=0)

        endpoint = f"/api/v0/leaderboard/badge/{badge.slug}?username=no_progress&signup_source=main"
        response = auth_client.get(endpoint)

        assert response.status_code == 200
        data = response.json()
        assert data["top10"] == []
        assert data["in_progress"] == []
        assert data["in_progress_rank"] is None


class TestCoursePointsView:
    def test_returns_course_points_for_requested_users(self, auth_client: APIClient) -> None:
        course_id = "course-v1:Org+Course+Run"
        u1 = GammaUserFactory(user_uid="cp_u1")
        u2 = GammaUserFactory(user_uid="cp_u2")
        GammaUserFactory(user_uid="cp_u3")  # requested but has no course points
        GammaUserCoursePointsFactory(gamma_user=u1, course_id=course_id, points=80)
        GammaUserCoursePointsFactory(gamma_user=u2, course_id=course_id, points=30)
        # points for a different course must be ignored
        GammaUserCoursePointsFactory(gamma_user=u1, course_id="course-v1:Org+Other+Run", points=999)

        response = auth_client.post(
            "/api/v0/course-points",
            {"course_id": course_id, "user_uids": ["cp_u1", "cp_u2", "cp_u3"]},
            format="json",
        )

        assert response.status_code == 200
        assert response.json() == {"cp_u1": 80, "cp_u2": 30}

    def test_empty_user_list_returns_empty_mapping(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            "/api/v0/course-points",
            {"course_id": "course-v1:Org+Course+Run", "user_uids": []},
            format="json",
        )
        assert response.status_code == 200
        assert response.json() == {}

    def test_unauthorized_request_is_forbidden(self, client: APIClient) -> None:
        response = client.post(
            "/api/v0/course-points",
            {"course_id": "course-v1:Org+Course+Run", "user_uids": ["cp_u1"]},
            format="json",
        )
        assert response.status_code == 403


class TestUsersLeaderBoardView:
    """
    Test Case for the UsersLeaderBoardView (a leaderboard restricted to a supplied
    set of users, ranked by points — used by the dashboard's country leaderboard).
    """

    ENDPOINT = "/api/v0/leaderboard/users"

    def test_unauthorized_request_is_forbidden(self, client: APIClient) -> None:
        response = client.post(
            self.ENDPOINT,
            {"username": "viewer", "signup_source": "main", "user_uids": ["a"]},
            format="json",
        )
        assert response.status_code == 403

    def test_ranks_requested_users_by_points(self, auth_client: APIClient) -> None:
        GammaUserFactory(user_uid="low", points=10, signup_source="main")
        GammaUserFactory(user_uid="high", points=90, signup_source="main")
        GammaUserFactory(user_uid="mid", points=50, signup_source="main")

        response = auth_client.post(
            self.ENDPOINT,
            {"username": "high", "signup_source": "main", "user_uids": ["low", "high", "mid"]},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        assert [member["user_uid"] for member in data["top10"]] == ["high", "mid", "low"]
        assert [member["points"] for member in data["top10"]] == [90, 50, 10]
        assert data["competitors"] == []
        # The requesting user ("high") leads, so their rank is 1.
        assert data["rank"] == 1

    def test_only_requested_users_are_returned(self, auth_client: APIClient) -> None:
        GammaUserFactory(user_uid="wanted", points=10, signup_source="main")
        GammaUserFactory(user_uid="unwanted", points=99, signup_source="main")

        response = auth_client.post(
            self.ENDPOINT,
            {"username": "wanted", "signup_source": "main", "user_uids": ["wanted"]},
            format="json",
        )

        assert response.status_code == 200
        assert [member["user_uid"] for member in response.json()["top10"]] == ["wanted"]

    def test_empty_user_list_returns_empty_leaderboard(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            self.ENDPOINT,
            {"username": "viewer", "signup_source": "main", "user_uids": []},
            format="json",
        )

        assert response.status_code == 200
        assert response.json() == {"top10": [], "competitors": [], "rank": None, "user_uid": "viewer"}

    def test_users_from_other_signup_sources_are_excluded(self, auth_client: APIClient) -> None:
        # The country page is scoped to the requesting user's signup source, mirroring
        # the regular leaderboard's per-source partitioning.
        GammaUserFactory(user_uid="same_site", points=10, signup_source="main")
        GammaUserFactory(user_uid="other_site", points=99, signup_source="OTHER")

        response = auth_client.post(
            self.ENDPOINT,
            {"username": "same_site", "signup_source": "main", "user_uids": ["same_site", "other_site"]},
            format="json",
        )

        assert response.status_code == 200
        assert [member["user_uid"] for member in response.json()["top10"]] == ["same_site"]

    def test_users_with_unset_signup_source_count_as_main(self, auth_client: APIClient) -> None:
        # A GammaUser with no signup source belongs to the MAIN leaderboard, so it is
        # matched when the requesting user's source is "main".
        GammaUserFactory(user_uid="legacy", points=42, signup_source=None)

        response = auth_client.post(
            self.ENDPOINT,
            {"username": "legacy", "signup_source": "main", "user_uids": ["legacy"]},
            format="json",
        )

        assert response.status_code == 200
        assert [member["user_uid"] for member in response.json()["top10"]] == ["legacy"]

    def test_rank_is_none_when_viewer_is_not_in_the_set(self, auth_client: APIClient) -> None:
        GammaUserFactory(user_uid="someone", points=10, signup_source="main")

        response = auth_client.post(
            self.ENDPOINT,
            {"username": "outsider", "signup_source": "main", "user_uids": ["someone"]},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        assert [member["user_uid"] for member in data["top10"]] == ["someone"]
        assert data["rank"] is None

    def test_members_are_limited_to_the_top_100(self, auth_client: APIClient, mocker: MockerFixture) -> None:
        mocker.patch.object(UsersLeaderBoardView, "MEMBERS_LIMIT", 2)
        for index in range(3):
            GammaUserFactory(user_uid=f"u{index}", points=index, signup_source="main")

        response = auth_client.post(
            self.ENDPOINT,
            {"username": "u2", "signup_source": "main", "user_uids": ["u0", "u1", "u2"]},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        # Only the top 2 users are serialized, but rank still reflects all matched users.
        assert [member["user_uid"] for member in data["top10"]] == ["u2", "u1"]
        assert data["rank"] == 1
