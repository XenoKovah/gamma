import logging

from django.core.cache import cache
from requests.exceptions import ConnectionError

from .client import EdxApiV2Client
from .exceptions import (
    EdxApiNotFoundException,
    EdxApiResponseParsingException,
    EdxApiServerErrorException,
    EdxApiUnauthorizedException,
    OtherEdxApiException,
)

log = logging.getLogger(__name__)

EVENTS_CACHE_KEY = 'gamma_events_list_response'


def get_gamma_events_list():
    events_list_response = cache.get(EVENTS_CACHE_KEY)
    if not events_list_response:
        client = EdxApiV2Client()
        try:
            events_list_response = client.get_events()
            cache.set(EVENTS_CACHE_KEY, events_list_response)
        except (
            EdxApiNotFoundException,
            EdxApiResponseParsingException,
            EdxApiServerErrorException,
            EdxApiUnauthorizedException,
            OtherEdxApiException,
            ConnectionError,
        ) as e:
            log.warning("Failed to get response from edx-integration: {}".format(e))
            events_list_response = []
    return events_list_response
