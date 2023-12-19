"""
Configuration module containing providers keys.
"""

from dataclasses import dataclass


@dataclass
class Config:
    """
    Auth data keys.
    """

    # OneSignal provider config
    ONE_SIGNAL_USER_AUTH_KEY: str = "one_signal_user_auth_key"
    ONE_SIGNAL_APP_AUTH_KEY:  str = "one_signal_app_auth_key"
    ONE_SIGNAL_APP_ID:        str = "one_signal_app_id"
    # Webpushr provider config
    WEBPUSHR_KEY:             str = "webpushr_key"
    WEBPUSHR_SECRET:          str = "webpushr_secret"
    # EDX custom notifications
    EDX_API_KEY:              str = "edx_api_key"
    # Formatting
    EDX_NOTIF_FORMAT_FUNC:    str = "edx_notif_format_func"


@dataclass
class Provider:
    """
    Providers name.
    """

    ONESIGNAL: int = 1
    WEBPUSHR:  int = 2
    EDX:       int = 3

@dataclass
class MESSAGE:
    """
    Message kind.
    """
    BADGE_AWARDED:  str = "badge_awarded"
    STATUS_AWARDED: str = "status_awarded"
    INFO_MSG:       str = "info_msg"
