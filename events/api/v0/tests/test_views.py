import pytest
from django.urls import reverse_lazy
from rest_framework import status

from core.utils import AppClientUtils
from events.models import Event

pytestmark = pytest.mark.django_db


class TestEventsAPI:
    """
    Test suite for creating an event via the 'EventsAPIView' view.
    """

    endpoint = reverse_lazy('events')

    def test_create_event_valid(self, auth_client, event_request_data):
        response = auth_client.post(self.endpoint, event_request_data)

        response_json = response.json()

        assert response.status_code == 201

        event = Event.objects.get(course_id=event_request_data.get('course_id'))

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

        response = auth_client.post(self.endpoint, event_request_data)

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

        response = auth_client.post(self.endpoint, event_request_data)

        response_json = response.json()

        assert response.status_code == 400
        assert 'The fields uid, client, username must make a unique set.' in response_json.get('non_field_errors')


@pytest.mark.no_rgg_events
class TestAvailableActionsAPI:
    """
    Test suite for get list of available actions to setup rules.
    """

    endpoint = reverse_lazy('available-actions')

    @pytest.mark.parametrize(
        'event_name, expected_schema, title',
        [
            (
                'problem_graded',
                {'field': 'count', 'title': 'Number of repetitions required', 'type': 'integer', 'required': True},
                'Award for problem graded'
            ),
            (
                'stop_video',
                {'field': 'count', 'title': 'Number of repetitions required', 'type': 'integer', 'required': True},
                'Award for stopping video'
            ),
            (
                'rgg_points_distribution',
                {'field': 'points', 'title': 'Number of points required', 'type': 'integer', 'required': True},
                'Award for points distribution'
            ),
        ],
        ids=[
            'Passed: edX event',
            'Passed: Common external event',
            'Passed: Points distribution'
        ]
    )
    def test_get_available_actions(
        self,
        client,
        event_configuration_factory,
        event_name,
        expected_schema,
        title
    ):
        event_configuration = event_configuration_factory(
            event_type__name=event_name,
            title=title,
        )

        response = client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json() == [{
            'event_name': event_configuration.event_name,
            'id': event_configuration.id,
            'title': event_configuration.title,
            'schema': [expected_schema]
        }]
