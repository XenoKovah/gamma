import pytest
from django.urls import reverse_lazy
from rest_framework import status

from events.models import Event

pytestmark = pytest.mark.django_db


class TestEventsAPI:
    """
    Test suite for creating an event via the 'EventsAPIView' view.
    """

    endpoint = reverse_lazy('events:api:v0:events')

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

        mock_app_client = mocker.MagicMock()
        mock_app_client.name = mock_client_uid
        mocker.patch('core.authentication.AppClient.objects.get', return_value=mock_app_client)

        event = event_factory(client=mock_client_uid)
        event_request_data['uid'] = event.uid
        event_request_data['client'] = event.client
        event_request_data['username'] = event.username

        response = auth_client.post(self.endpoint, event_request_data)

        response_json = response.json()

        assert response.status_code == 400
        assert 'The fields uid, client, username must make a unique set.' in response_json.get('non_field_errors')

    def test_create_event_stores_block_id(self, auth_client, event_request_data):
        block_id = 'block-v1:edx+101+101+type@done+block@aaaa'
        event_request_data['block_id'] = block_id

        response = auth_client.post(self.endpoint, event_request_data)

        assert response.status_code == 201
        event = Event.objects.get(uid=event_request_data['uid'])
        assert event.block_id == block_id

    def test_duplicate_event_records_block_id_on_legacy_row(
        self, auth_client, event_request_data, event_factory, mocker
    ):
        """
        Rows ingested before block_id existed get it filled in when the same logical
        event is re-sent (the done-state backfill path); the duplicate is still rejected.
        """
        mock_client_uid = 'mock_client_uid'
        block_id = 'block-v1:edx+101+101+type@done+block@bbbb'

        mock_app_client = mocker.MagicMock()
        mock_app_client.name = mock_client_uid
        mocker.patch('core.authentication.AppClient.objects.get', return_value=mock_app_client)

        event = event_factory(client=mock_client_uid, block_id=None)
        event_request_data['uid'] = event.uid
        event_request_data['username'] = event.username
        event_request_data['block_id'] = block_id

        response = auth_client.post(self.endpoint, event_request_data)

        assert response.status_code == 400
        event.refresh_from_db()
        assert event.block_id == block_id

    def test_duplicate_event_does_not_overwrite_existing_block_id(
        self, auth_client, event_request_data, event_factory, mocker
    ):
        mock_client_uid = 'mock_client_uid'
        original_block_id = 'block-v1:edx+101+101+type@done+block@cccc'

        mock_app_client = mocker.MagicMock()
        mock_app_client.name = mock_client_uid
        mocker.patch('core.authentication.AppClient.objects.get', return_value=mock_app_client)

        event = event_factory(client=mock_client_uid, block_id=original_block_id)
        event_request_data['uid'] = event.uid
        event_request_data['username'] = event.username
        event_request_data['block_id'] = 'block-v1:edx+101+101+type@done+block@dddd'

        response = auth_client.post(self.endpoint, event_request_data)

        assert response.status_code == 400
        event.refresh_from_db()
        assert event.block_id == original_block_id

    def test_create_event_honors_explicit_created_at(self, auth_client, event_request_data):
        event_request_data['created_at'] = '2025-03-04T05:06:07Z'

        response = auth_client.post(self.endpoint, event_request_data)

        assert response.status_code == 201
        event = Event.objects.get(uid=event_request_data['uid'])
        assert event.created_at.isoformat() == '2025-03-04T05:06:07+00:00'


@pytest.mark.no_rgg_events
class TestAvailableActionsAPI:
    """
    Test suite for get list of available actions to setup rules.
    """

    endpoint = reverse_lazy('events:api:v0:available-actions')

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
