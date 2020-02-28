"""
Custom edX API exceptions.
"""

import http.client


class EdxApiException(Exception):
    """
    Base class for edX API exceptions.

    Subclasses should provide `.default_msg` and `.status_code` properties.
    """

    default_msg = "An edX API exception occurred."
    status_code = http.client.EXPECTATION_FAILED

    def __init__(self, message=None):
        """
        Initialization of exceptions base class object.
        """
        self.message = message or self.default_msg
        super().__init__(message)

    def __str__(self):
        """
        Override string representation of exceptions base class object.
        """
        return self.message


class EdxApiResponseParsingException(EdxApiException):
    """
    Custom exception occurring when API client response parsing.
    """

    default_msg = "Can't parse unexpected response during POST request to edX API."
    status_code = http.client.INTERNAL_SERVER_ERROR


class EdxApiUnauthorizedException(EdxApiException):
    """
    Custom exception occurring when an unauthorized call is made to edX API.
    """

    default_msg = "Unauthorized call to edX API."
    status_code = http.client.UNAUTHORIZED


class EdxApiNotFoundException(EdxApiException):
    """
    Custom exception occurring when a Not Found status is received from edX API.
    """

    default_msg = "Not Found status received from edX API."
    status_code = http.client.NOT_FOUND


class EdxApiServerErrorException(EdxApiException):
    """
    Custom exception occurring when a Server Error status is received from edX API.
    """

    default_msg = "Server Error status received from edX API."
    status_code = http.client.INTERNAL_SERVER_ERROR


class EdxApiResponseTimeoutException(EdxApiException):
    """
    Custom exception occurring when edX API request is Timed Out.
    """
    default_msg = "Timeout for edX API request."
    status_code = http.client.REQUEST_TIMEOUT


class OtherEdxApiException(EdxApiException):
    """
    Unclassified edX API exception.
    """

    default_msg = "Other edX API exception occurred."
    status_code = http.client.EXPECTATION_FAILED
