from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core import db
from core.authentication import KeySecretAuthentication


class LeaderBoardView(APIView):
    """
    Return leaderbord data.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request):
        user_uid = request.GET.get('username')
        user_signup_source = request.GET.get('signup_source')

        leaders, competitors, rank = db.leaders.read_for_user(user_uid, user_signup_source)

        system_statuses = db.statuses.read()

        return Response({
            'top10': leaders.to_primitive('roster').get('roster'),
            'rank': rank,
            'user_uid': user_uid,
            'competitors': competitors.to_primitive('roster').get('roster') if competitors else [],
            'system_statuses': [status.to_primitive('public') for status in system_statuses]
        }, status=status.HTTP_200_OK, content_type='application/json')
