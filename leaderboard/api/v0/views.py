from typing import Optional

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import KeySecretAuthentication
from leaderboard.constants import GENERAL_LEADERBOARD_ID_TEMPLATE
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
        user_signup_source = request.GET.get("signup_source")

        GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)

        response_data = self._collect_response_data(user_uid, user_signup_source)

        return Response(response_data, status=status.HTTP_200_OK)

    def _collect_response_data(self, user_uid: Optional[str], user_signup_source: Optional[str]) -> dict:
        redis_leaderboard_repo = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        user_signup_source = user_signup_source or settings.MAIN_SIGNUP_SOURCE
        leaderboard_id = GENERAL_LEADERBOARD_ID_TEMPLATE.format(user_signup_source=user_signup_source)
        leaders, competitors, rank = GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repo,
            leaderboard_member_data_repository,
        ).execute(leaderboard_id, user_uid)

        return {
            "top10": leaders,
            "rank": rank,
            "user_uid": user_uid,
            "competitors": competitors,
        }
