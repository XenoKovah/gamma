import logging

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache
from requests.exceptions import ConnectionError

from .client import EdxApiV2Client
from .exceptions import (
    EdxApiNotFoundException,
    EdxApiResponseParsingException,
    EdxApiResponseTimeoutException,
    EdxApiServerErrorException,
    EdxApiUnauthorizedException,
    OtherEdxApiException,
)

log = logging.getLogger(__name__)

EVENTS_CACHE_KEY = 'gamma_events_list_response'
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def get_gamma_events_list():
    """
    Wrapper for EdxApiV2Client get_events method.

    Cache client response and process it's exceptions.
    """
    events_list_response = cache.get(EVENTS_CACHE_KEY)
    if not events_list_response:
        client = EdxApiV2Client()
        try:
            events_list_response = client.get_events(timeout=20)
            cache.set(EVENTS_CACHE_KEY, events_list_response, CACHE_TTL)
        except (
            EdxApiNotFoundException,
            EdxApiResponseParsingException,
            EdxApiResponseTimeoutException,
            EdxApiServerErrorException,
            EdxApiUnauthorizedException,
            OtherEdxApiException,
            ConnectionError,
        ) as e:
            log.warning(f"Failed to get response from edx-integration: {e}")
            events_list_response = []
    return events_list_response
