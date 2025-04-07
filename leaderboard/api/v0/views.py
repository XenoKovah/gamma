from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import KeySecretAuthentication
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.repository import ORMLeaderboardMemberDataRepository, RedisLeaderboardRepository
from leaderboard.usecases import GetPersonalizedLeaderboardUseCase
from users.models import GammaUser


class LeaderBoardView(APIView):
    """
    Provide personalized leaderboard data for the requesting Gamma user.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request):
        user_uid = request.GET.get("username")
        leaderboard_retrieving_context = LeaderboardRetrievingContext(
            user_uid,
            request.GET.get("signup_source"),
            request.GET.get("course_id"),
        )

        GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)

        response_data = self._collect_response_data(leaderboard_retrieving_context)

        return Response(response_data, status=status.HTTP_200_OK)

    def _collect_response_data(self, leaderboard_retrieving_context: LeaderboardRetrievingContext) -> dict:
        """
        Collect data to place in the response body.
        """
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        leaders, competitors, rank = GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        ).execute(leaderboard_retrieving_context)

        return {
            "top10": leaders,
            "rank": rank,
            "user_uid": leaderboard_retrieving_context.user_uid,
            "competitors": competitors,
        }
