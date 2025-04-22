"""
Authorization unittests.
"""
import pytest

from core.notif.cfg import Config, Provider


pytestmark = pytest.mark.django_db


cfg = {
    Config.ONE_SIGNAL_APP_AUTH_KEY: Config.ONE_SIGNAL_APP_AUTH_KEY,
    Config.ONE_SIGNAL_APP_ID: Config.ONE_SIGNAL_APP_ID,
    Config.WEBPUSHR_KEY: Config.WEBPUSHR_KEY,
    Config.WEBPUSHR_SECRET: Config.WEBPUSHR_SECRET,
}


PATH_AUTHORIZE = "core.notif.onesignal_provider.OneSignalServiceBuilder.authorize"
PATH_ONESIGNAL_SDK_CLIENT = "core.notif.onesignal_provider.onesignal_sdk.Client"


@pytest.mark.unittests
def test_onesignal_builder(push_factory, mocker):
    """
    Ensure getting onesignal provider include authorization step.


    Also check singleton pattern usage.
    """
    _authorize = mocker.patch(PATH_AUTHORIZE)

    _ = push_factory.get(Provider.ONESIGNAL, **cfg)
    # Check singleton pattern
    _ = push_factory.get(Provider.ONESIGNAL, **cfg)

    _authorize.assert_called_once_with(cfg[Config.ONE_SIGNAL_APP_AUTH_KEY],
                                       cfg[Config.ONE_SIGNAL_APP_ID])


@pytest.mark.unittests
def test_onesignal_authorize(push_factory, mocker):
    """
    Ensure getting onesignal provider invoke onesignal_sdk.Client usage.
    """
    _onesignal_client = mocker.patch(PATH_ONESIGNAL_SDK_CLIENT)

    _ = push_factory.get(Provider.ONESIGNAL, **cfg)

    _onesignal_client.assert_called_once_with(app_auth_key=cfg[Config.ONE_SIGNAL_APP_AUTH_KEY],
                                              app_id=cfg[Config.ONE_SIGNAL_APP_ID])
