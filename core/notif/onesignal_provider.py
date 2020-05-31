"""
OneSignal provider module.
"""

import onesignal as onesignal_sdk

from core.notif.models import OneSignalNotif


class OneSignalService:
    """
    OneSignal concrete provider implementation.

    Usage:
    ---
    from core.notif import push
    from core.notif.cfg import Config, Provider

    from core import db


    cfg = {
        Config.ONE_SIGNAL_APP_AUTH_KEY: "app_auth_key",
        Config.ONE_SIGNAL_APP_ID: "app_id",
        ...
    }


    onesignal_provider = push.factory.get(Provider.ONESIGNAL, **cfg)

    user1 = db.read_user("username1")
    badge = db.read_badge_as_ob("badge_uid")

    heading = "Message heading"
    content = "Hello username"

    data = {
        "head": heading,             # required
        "body": content,             # required
        "lang": "en",                # required
        "icon": badge.url,           # not required
        "url":  "http://localhost"   # not required
    }


    result = onesignal_provider.send_notif(user, data)
    assert isinstance(result, dict)
    """
    def __init__(self, onesignal_client):
        self._client = onesignal_client

    @staticmethod
    def _create_base_notif_ob(data):
        return OneSignalNotif().import_data(data)

    def _create_notif(self, notif):
        new_notif = onesignal_sdk.Notification(post_body=notif.to_native("public"))
        return new_notif

    def _create_base_notif(self, data):
        """
        Notification for player ids.

        hhttps://documentation.onesignal.com/reference/create-notification#send-to-specific-devices
        """
        lang = data.get("lang", "en")
        headings = {lang: data.get("head")}
        contents = {lang: data.get("body")}

        notif = self._create_base_notif_ob({
            "contents": contents,
            "headings": headings,
            "chrome_web_icon": data.get("icon"),
            "url": data.get("url"),
        })

        return notif

    def send_notif(self, user, data):
        """
        Sending notification by user_id (currently username) or by player_ids.
        """
        result = []

        _notif = self._create_base_notif(data)

        with _notif.as_include_external_user_ids(user) as externalized_notif:
            response = self._client.send_notification(self._create_notif(externalized_notif))
            result.append(response)

        return result


class OneSignalServiceBuilder:
    """
    OneSignal specific builder.
    """
    def __init__(self):
        self._instance = None

    def __call__(self, one_signal_app_auth_key, one_signal_app_id, **_ignored):
        """
        Call authorize method, save client and return it.
        """
        if not self._instance:
            onesignal_client = self.authorize(one_signal_app_auth_key, one_signal_app_id)

            self._instance = OneSignalService(onesignal_client)

        return self._instance

    def authorize(self, app_auth_key, app_id):
        """
        Create OneSignal authorized client.
        """
        onesignal_client = onesignal_sdk.Client(app_auth_key=app_auth_key, app_id=app_id)

        return onesignal_client
