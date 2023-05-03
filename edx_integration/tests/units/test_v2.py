import pytest  # pylint: disable=import-error
from django.conf import settings

from edx_integration.api.v2.client import EdxNotificationClient


@pytest.mark.unittests
def test_edx_notification_client_init():
    test_key = "test_key"

    assert EdxNotificationClient().api_key == settings.EDX_API_KEY
    assert EdxNotificationClient(test_key).api_key == test_key


@pytest.mark.unittests
def test_edx_notification_client_send(mocker, notif_data):
    mocked_post = mocker.patch("edx_integration.api.v2.client.EdxNotificationClient.post")

    client = EdxNotificationClient()
    client.send_notification(notif_data)

    mocked_post.assert_called_once_with(client.base_url, data=notif_data, timeout=None)
