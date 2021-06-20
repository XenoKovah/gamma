"""
Unittests for push notification providers.
"""
import pytest
from django.test import override_settings

from core.notif.cfg import Config, Provider


cfg = {
    Config.ONE_SIGNAL_APP_AUTH_KEY: Config.ONE_SIGNAL_APP_AUTH_KEY,
    Config.ONE_SIGNAL_APP_ID: Config.ONE_SIGNAL_APP_ID,
    Config.WEBPUSHR_KEY: Config.WEBPUSHR_KEY,
    Config.WEBPUSHR_SECRET: Config.WEBPUSHR_SECRET,
    Config.EDX_API_KEY: Config.EDX_API_KEY,
}


PATH_AUTHORIZE         = "core.notif.edx_provider.EdxServiceBuilder.authorize"
PATH_CREATE_BASE_NOTIF = "core.notif.edx_provider.EdxService._create_base_notif"
PATH_EDX_CLIENT        = "core.notif.edx_provider.EdxNotificationClient"


@pytest.mark.unittests
def test_send_notif(push_factory, notif_data, user, mocker):
    """
    Check sending.
    """
    _base_notif = mocker.Mock()
    _edx_client = mocker.patch(PATH_EDX_CLIENT)
    mocker.patch(PATH_AUTHORIZE, return_value=_edx_client)
    _create_base_notif = mocker.patch(PATH_CREATE_BASE_NOTIF, return_value=_base_notif)

    edx_provider = push_factory.get(Provider.EDX, **cfg)
    result = edx_provider.send_notif(user, notif_data)

    # Check base notif creation
    _create_base_notif.assert_called_once_with(user, notif_data)
    _edx_client.send_notification.assert_called_once_with(_base_notif.to_primitive())

    assert isinstance(result, type(_edx_client.send_notification()))


@pytest.mark.unittests
def test_disabled_send_notif(push_factory, notif_data, user, mocker):
    """
    Check sending is disabled.
    """
    _base_notif = mocker.Mock()
    _edx_client = mocker.patch(PATH_EDX_CLIENT)
    mocker.patch(PATH_AUTHORIZE, return_value=_edx_client)
    _create_base_notif = mocker.patch(PATH_CREATE_BASE_NOTIF, return_value=_base_notif)

    with override_settings(EDX_NOTIFICATION_ENABLED=False):
        edx_provider = push_factory.get(Provider.EDX, **cfg)
        edx_provider.send_notif(user, notif_data)
        assert _create_base_notif.call_count == 0


@pytest.mark.unittests
def test__create_base_notif(push_factory, user, notif_data):
    edx_provider = push_factory.get(Provider.EDX, **cfg)
    notif = edx_provider._create_base_notif(user, notif_data)

    assert notif.recipients == [user.user_uid]
    assert notif.icon_url == notif_data['icon']
    assert notif.url == notif_data['url']
    assert notif.message is not None
    assert notif.source == "gamma"
    assert notif.save_notification


@pytest.mark.unittests
def test__format_message(push_factory, notif_data):
    edx_provider = push_factory.get(Provider.EDX, **cfg)
    text = edx_provider._format_message(notif_data)

    assert text == f'{ notif_data.get("head") } \n { notif_data.get("body") }'


@pytest.mark.unittests
def test__format_message_broken_head(push_factory, notif_data):
    edx_provider = push_factory.get(Provider.EDX, **cfg)

    del notif_data["head"]
    text = edx_provider._format_message(notif_data)

    assert text == notif_data.get("body")


@pytest.mark.unittests
def test__format_message_broken_body(push_factory, notif_data):
    edx_provider = push_factory.get(Provider.EDX, **cfg)

    del notif_data["body"]
    text = edx_provider._format_message(notif_data)

    assert text == notif_data.get("head")
