"""
Edx Notifications provider.
"""
from django.conf import settings

from edx_integration.api.v2.client import EdxNotificationClient
from core.notif.models import EdxNotif


class EdxService:
    """
    Edx Notification profider implemewntation.

    Usage:
    ---
    from core.notif import push
    from core.notif.cfg import Config, Provider

    from core import db


    cfg = {
        Config.EDX_API_KEY: environ.get("EDX_API_KEY"),
        ...
    }


    edx_provider = push.factory.get(Provider.EDX, **cfg)

    user = db.users.read_one("username1")
    badge = db.badges.read_one("badge_uid")

    heading = "Message heading"
    content = "Hello username"

    data = {
        "head": heading,             # required
        "body": content,             # required
        "lang": "en",                # required
        "icon": badge.url,           # not required
        "url":  "http://localhost"   # not required
    }


    result = edx_provider.send_notif(user, data)
    assert isinstance(result, dict)
    """

    def __init__(self, edx_client, format_func=None):
        self._client = edx_client
        self.__format_func = format_func

    @staticmethod
    def _create_base_notif_ob(data):
        notif = EdxNotif(data)
        notif.validate()

        return notif

    @staticmethod
    def __default_format(data):
        head = data.get("head")
        body = data.get("body")

        if head and body:
            return f'{ data.get("head") } \n { data.get("body") }'

        return data.get("head") or data.get("body")

    def _format_message(self, data):
        """
        Format full message.
        """
        if not self.__format_func:
            return self.__default_format(data)

        return self.__format_func(data)

    def _create_base_notif(self, user, data):
        """
        Customize notif content before object creation.
        """
        notif = self._create_base_notif_ob({
            "recipients": [user.user_uid],
            "message": self._format_message(data),
            "icon_url": data.get("icon"),
            "url": data.get("url"),
        })

        return notif

    def send_notif(self, user, data):  # pylint: disable=inconsistent-return-statements
        """
        Send notification by user_id (currently username) or by player_ids.
        """
        if not settings.EDX_NOTIFICATION_ENABLED:
            return

        _notif = self._create_base_notif(user, data)

        return self._client.send_notification(_notif.to_primitive("public"))


class EdxServiceBuilder:
    """
    Edx Notification specific builder.
    """

    def __init__(self):
        self._instance = None

    def __call__(self, edx_api_key, **_ignored):
        """
        Create Edx client and return it.
        """
        if not self._instance:
            edx_client = self.authorize(edx_api_key)

            self._instance = EdxService(edx_client)

        return self._instance

    def authorize(self, edx_api_key):
        """
        Create EDX_API_KEY based client.
        """
        edx_client = EdxNotificationClient(api_key=edx_api_key)

        return edx_client
