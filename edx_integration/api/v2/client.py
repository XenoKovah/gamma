"""
Integration with edX REST API v2 clients.
"""

import json
import http.client
import urllib.parse

from django.conf import settings
import requests

from .exceptions import (
    EdxApiNotFoundException,
    EdxApiResponseParsingException,
    EdxApiResponseTimeoutException,
    EdxApiServerErrorException,
    EdxApiUnauthorizedException,
    OtherEdxApiException,
)


class EdxApiBaseClient(object):
    """
    Low level edX API client.
    """

    def __init__(self, api_key=None):
        """
        Initialize a low-level edX API client.

        Arguments:
            api_key (str): edx API key required for authorization.
        """
        self.api_key = api_key or settings.EDX_API_KEY

    def get(self, url, headers=None, timeout=None):
        """
        Issue REST GET request to a given URL.

        Arguments:
            url (str): API url to fetch a resource from.
            headers (dict): Headers necessary as per API.
            timeout (int): Set request timeout in seconds if not None.
        Returns:
            endpoint response with custom data (dict).
        """
        _headers = {
            "content-type": "application/json",
            "X-Edx-Api-Key": self.api_key,
        }
        if headers is not None:
            _headers.update(headers)
        try:
            resp = requests.get(url, headers=_headers, timeout=timeout)

            if resp.status_code == http.client.OK:
                return resp.json()
            elif resp.status_code == http.client.UNAUTHORIZED:
                raise EdxApiUnauthorizedException
            elif resp.status_code == http.client.INTERNAL_SERVER_ERROR:
                raise EdxApiServerErrorException
            elif resp.status_code == http.client.NOT_FOUND:
                raise EdxApiNotFoundException
            else:
                raise OtherEdxApiException
        except requests.exceptions.ReadTimeout:
            raise EdxApiResponseTimeoutException
        except ValueError:
            raise EdxApiResponseParsingException
    
    def post(self, url, data=None, headers=None, timeout=None):
        """
        Issue REST POST request to a given URL.

        Arguments:
            url (str): API url to post data to.
            data (dict): data to post
            headers (dict): Headers necessary as per API.
            timeout (int): Set request timeout in seconds if not None.
        Returns:
            endpoint response with custom data (dict).
        """
        _headers = {
            "content-type": "application/json",
            "X-Edx-Api-Key": self.api_key,
        }
        if headers is not None:
            _headers.update(headers)
        if data is not None:
            _data = json.dumps(data)
        try:
            resp = requests.post(url, data=_data, headers=_headers, timeout=timeout)

            if resp.status_code == http.client.OK:
                return resp.json()
            elif resp.status_code == http.client.UNAUTHORIZED:
                raise EdxApiUnauthorizedException
            elif resp.status_code == http.client.INTERNAL_SERVER_ERROR:
                raise EdxApiServerErrorException
            elif resp.status_code == http.client.NOT_FOUND:
                raise EdxApiNotFoundException
            else:
                raise OtherEdxApiException
        except requests.exceptions.ReadTimeout:
            raise EdxApiResponseTimeoutException
        except ValueError:
            raise EdxApiResponseParsingException


class EdxApiV2Client(EdxApiBaseClient):
    """
    Encapsulate API logic for specific edX API v2 features.
    """

    def __init__(self, api_key=None, base_url=None):
        """
        Initialize a high-level edX API v2 client.

        Arguments:
            api_key (str): edx API key required for authorization.
            base_url (str): base URL of API calls.
        """
        self.base_url = base_url or urllib.parse.urljoin(settings.EDX_LMS_BASE_URL, settings.EDX_API_V2_SUFFIX)
        super(EdxApiV2Client, self).__init__(api_key)

    def get_courses(self):
        """
        Get edX courses.

        Returns:
            courses (list): list of courses. Course format derives from `SlashSeparatedCourseKey`,
                similarly to the `course_id` in the tracking flow,
                ref.: https://edx.readthedocs.io/projects/devdata/en/stable/internal_data_formats/tracking_logs.html
                Example:
                ```
                [
                    "edx/AN101/2014_T1",
                    "rg/BA102/2019_T4"
                ]
                ```
        """
        url = self.base_url + "courses/"
        # NOTE: consider validating the response (here and in other cases)
        return self.get(url)

    def get_organizations(self):
        """
        Get edX organizations.

        Returns:
            organizations (list): list of organizations.
                Example:
                ```
                [
                    "edx",
                    "rg"
                ]
                ```
        """
        url = self.base_url + "organizations/"
        return self.get(url)

    def get_events(self, timeout=None):
        """
        Get edX event list that could be sent to gamma.

        Returns:
            events (list): list of events.
                Example:
                ```
                [
                    {
                        "verbose_name": "Get Certificate for Course",
                        "event_type": "edx_certificate_created"
                    },
                    {
                        "verbose_name": "Show Video Transcript",
                        "event_type": "edx_video_transcript_shown"
                    }
                ]
                ```
        """
        url = self.base_url + "tracking-events-list/"
        return self.get(url, timeout=timeout)


class EdxNotificationClient(EdxApiBaseClient):
    """
    EdX base notification client.
    """
    def __init__(self, api_key=None, base_url=None):
        """
        Initialize a high-level edX API v2 client.

        Arguments:
            api_key (str): edx API key required for authorization.
            base_url (str): base URL of API calls.
        """
        self.base_url = base_url or urllib.parse.urljoin(settings.EDX_LMS_BASE_URL, settings.EDX_NOTIFICATION_API_SUFFIX)
        super().__init__(api_key)

    def send_notification(self, data, timeout=None):
        """
        Send prepared notification.
        """
        # This is for future modifications
        url = self.base_url
        return self.post(url, data=data, timeout=timeout)
