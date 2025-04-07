import urllib.parse
from typing import Type
from unittest.mock import MagicMock, Mock, patch

import pytest
from pytest_mock.plugin import MockerFixture
from rest_framework.test import APIClient

from leaderboard.api.v0.views import LeaderBoardView
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.factories import LeaderboardRetrievingContextFactory
from users.models import GammaUser


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
