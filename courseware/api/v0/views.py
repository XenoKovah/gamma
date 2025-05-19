from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from edx_integration.api.v2.client import EdxApiV2Client
from edx_integration.api.v2.exceptions import (
    EdxApiNotFoundException,
    EdxApiResponseParsingException,
    EdxApiServerErrorException,
    EdxApiUnauthorizedException,
    OtherEdxApiException,
)


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class CoursesView(APIView):
    """
    Courses list from edx-platform.
    """

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, __) -> Response:
        client = EdxApiV2Client()
        try:
            return Response(
                {'courses': client.get_courses()},
                status=status.HTTP_200_OK
            )
        except (
            EdxApiNotFoundException,
            EdxApiResponseParsingException,
            EdxApiServerErrorException,
            EdxApiUnauthorizedException,
            OtherEdxApiException,
        ) as e:
            return Response(
                {'courses': []},
                status=e.status_code
            )


class OrganizationsView(APIView):
    """
    Existing organizations from edx-platform.
    """

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, __) -> Response:
        client = EdxApiV2Client()
        try:
            return Response(
                {'organizations': client.get_organizations()},
                status=status.HTTP_200_OK
            )
        except (
            EdxApiNotFoundException,
            EdxApiResponseParsingException,
            EdxApiServerErrorException,
            EdxApiUnauthorizedException,
            OtherEdxApiException,
        ) as e:
            return Response(
                {'organizations': []},
                status=e.status_code
            )
