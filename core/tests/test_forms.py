import json

from django.core.cache import cache
from django.forms import modelform_factory

from achievements.forms import EventForm as BaseEventForm
from achievements.models import Event
from edx_integration.api.v2.utils import EVENTS_CACHE_KEY

import requests

EventForm = modelform_factory(
    Event,
    BaseEventForm,
    # fields are got from achievments.admin.EventAdmin
    fields=('event_type', 'award', 'title', 'color', 'notification_message')
)


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def _clear_events_cache():
    cache.delete(EVENTS_CACHE_KEY)


def teardown_module(module):
    _clear_events_cache()  # fix local deployment cache substituted by test values


def test_event_form_events_get_success(monkeypatch, db):
    _clear_events_cache()
    mock_data_dict = [
        {
            "verbose_name": "Test Event 1",
            "event_type": "test1event"
        },
        {
            "verbose_name": "Test Event 2",
            "event_type": "test2event"
        }
    ]

    def mock_get(*args, **kwargs):
        class MockResponseData(MockResponse):
            @staticmethod
            def json():
                return mock_data_dict

        return MockResponseData(status_code=200)

    monkeypatch.setattr(
        requests,
        'get',
        mock_get
    )
    form = EventForm()

    expected_data = {'test1event': 'Test Event 1', 'test2event': 'Test Event 2'}
    assert form['event_type'].field.widget.attrs['data-event-names'] == json.dumps(expected_data)
    expected_choices = [('test1event', 'test1event'), ('test2event', 'test2event')]
    assert form['event_type'].field.widget.choices == expected_choices


def test_event_form_events_get_error(monkeypatch, db):
    _clear_events_cache()

    def mock_get(*args, **kwargs):
        return MockResponse(status_code=403)

    monkeypatch.setattr(
        requests,
        'get',
        mock_get
    )
    form = EventForm()
    assert form['event_type'].field.widget.attrs.get('data-event-names') is None
    assert not hasattr(form['event_type'].field.widget, 'choices')


def test_event_form_events_existed(monkeypatch, db):
    _clear_events_cache()
    Event.objects.create(event_type="test1event", award=1)
    Event.objects.create(event_type="test2event", award=2)
    mock_data_dict = [
        {
            "verbose_name": "Test Event 1",
            "event_type": "test1event"
        },
        {
            "verbose_name": "Test Event 2",
            "event_type": "test2event"
        },
        {
            "verbose_name": "Test Event 3",
            "event_type": "test3event"
        }
    ]

    def mock_get(*args, **kwargs):
        class MockResponseData(MockResponse):
            @staticmethod
            def json():
                return mock_data_dict

        return MockResponseData(status_code=200)

    monkeypatch.setattr(
        requests,
        'get',
        mock_get
    )
    form = EventForm()

    expected_data = {'test3event': 'Test Event 3'}
    assert form['event_type'].field.widget.attrs['data-event-names'] == json.dumps(expected_data)
    expected_choices = [('test3event', 'test3event'), ]
    assert form['event_type'].field.widget.choices == expected_choices


def test_event_form_edit(db):
    test_event = Event.objects.create(
        event_type="test1event", award=1, title='Test Event'
    )
    edit_data = {
        'event_type': 'test1event',
        'title': 'Test Event [Edited]',
        'award': 3, 'color': 1, 'notification_message': 'You have got {} point.',
    }
    edit_form = EventForm(edit_data, instance=test_event)

    assert edit_form['event_type'].field.widget.attrs.get('readonly') is True
    assert edit_form.is_valid() is True
    edit_form.save()

    after_editing_event = Event.objects.get(event_type='test1event')

    assert after_editing_event.title == edit_data['title']
    assert after_editing_event.award == edit_data['award']
