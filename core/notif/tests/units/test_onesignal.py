"""
Unittests for push notification providers.
"""
import pytest

from core.notif.cfg import Config, Provider
from core.notif.models import OneSignalNotif as Notif


pytestmark = pytest.mark.django_db


cfg = {
    Config.ONE_SIGNAL_APP_AUTH_KEY: Config.ONE_SIGNAL_APP_AUTH_KEY,
    Config.ONE_SIGNAL_APP_ID: Config.ONE_SIGNAL_APP_ID,
    Config.WEBPUSHR_KEY: Config.WEBPUSHR_KEY,
    Config.WEBPUSHR_SECRET: Config.WEBPUSHR_SECRET,
}


PATH_AUTHORIZE = "core.notif.onesignal_provider.OneSignalServiceBuilder.authorize"
PATH_CREATE_NOTIF = "core.notif.onesignal_provider.OneSignalService._create_notif"
PATH_CREATE_BASE_NOTIF = "core.notif.onesignal_provider.OneSignalService._create_base_notif"
PATH_DIRECT_NOTIF_OB = "core.notif.onesignal_provider.OneSignalService._create_direct_notif_ob"
PATH_ONESIGNAL_SDK_NOTIFICATION = "core.notif.onesignal_provider.onesignal_sdk.Notification"


@pytest.mark.unittests
def test_send_notif(push_factory, notif_data, user, mocker):
    """
    Check sending.
    """
    _one_signal_client = mocker.Mock()
    mocker.patch(PATH_AUTHORIZE, return_value=_one_signal_client)
    _create_base_notif = mocker.patch(PATH_CREATE_BASE_NOTIF)
    _create_notif = mocker.patch(PATH_CREATE_NOTIF)

    onesignal_provider = push_factory.get(Provider.ONESIGNAL, **cfg)
    result = onesignal_provider.send_notif(user, notif_data)

    # Check base notif creation
    _create_base_notif.assert_called_once_with(notif_data)
    # Check contextmanager usage
    _create_notif.assert_called_once_with(_create_base_notif().as_include_external_user_ids().__enter__())
    # Check _create_notif usage
    _one_signal_client.send_notification.assert_called_once_with(_create_notif())

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == _one_signal_client.send_notification()


@pytest.mark.unittests
def test__create_base_notif(push_factory, notif_data, user, mocker):
    """
    Check base notif object creation.
    """
    mocker.patch(PATH_AUTHORIZE, return_value=mocker.Mock())

    onesignal_provider = push_factory.get(Provider.ONESIGNAL, **cfg)
    base_notif_object = onesignal_provider._create_base_notif(notif_data)

    assert isinstance(base_notif_object, Notif)
    assert "include_external_user_ids" not in base_notif_object.to_native("public")
    assert "include_player_ids" not in base_notif_object.to_native("public")
    assert notif_data["head"] == base_notif_object.headings["en"]
    assert notif_data["body"] == base_notif_object.contents["en"]
    assert notif_data["icon"] == base_notif_object.chrome_web_icon
    assert notif_data["url"] == base_notif_object.url


@pytest.mark.unittests
def test_create_notif(push_factory, mocker):
    """
    Check _create_notif.
    """
    mocker.patch(PATH_AUTHORIZE, return_value=mocker.Mock())
    _onesignal_sdk_notification = mocker.patch(PATH_ONESIGNAL_SDK_NOTIFICATION)
    _notif = mocker.Mock()

    onesignal_provider = push_factory.get(Provider.ONESIGNAL, **cfg)
    _ = onesignal_provider._create_notif(_notif)

    _onesignal_sdk_notification.assert_called_once_with(post_body=_notif.to_native("public"))
