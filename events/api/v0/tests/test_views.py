import pytest
from django.urls import reverse_lazy

from core.utils import AppClientUtils
from events.models import Event


@pytest.mark.django_db
class TestCreateEvent:
    """
    Test suite for creating an event via the 'EventsAPIView' view.
    """

    endpoint = 'events'

    def test_create_event_valid(self, auth_client, event_request_data):
        response = auth_client.post(reverse_lazy(self.endpoint), event_request_data)

        response_json = response.json()

        assert response.status_code == 201

        event = Event.objects.last()
        assert Event.objects.count() == 1

        assert event.course_id == event_request_data['course_id']
        assert event.uid == event_request_data['uid']
        assert event.signup_source == event_request_data['signup_source']
        assert event.username == event_request_data['username']
        assert event.org == event_request_data['org']

        assert 'configuration' in response_json
        configuration = event.configuration
        assert configuration.event_name == event_request_data['event_type']

    def test_create_event_with_invalid_event_type(self, auth_client, event_request_data):
        field_name = 'event_type'
        event_request_data[field_name] = 'invalid_event_type'

        response = auth_client.post(reverse_lazy('events'), event_request_data)

        response_json = response.json()

        assert response.status_code == 400
        assert 'Error: Event type is not recognizable' in response_json.get(field_name)

    def test_create_event_already_exists(self, auth_client, event_request_data, event_factory, mocker):
        mock_client_uid = 'mock_client_uid'

        mock_app_client = mocker.MagicMock(uid=mock_client_uid)
        mocker.patch.object(AppClientUtils, 'get_app_client', return_value=mock_app_client)

        event = event_factory(client=mock_client_uid)
        event_request_data['uid'] = event.uid
        event_request_data['client'] = event.client
        event_request_data['username'] = event.username

        response = auth_client.post(reverse_lazy('events'), event_request_data)

        response_json = response.json()

        assert response.status_code == 400
        assert 'The fields uid, client, username must make a unique set.' in response_json.get('non_field_errors')
