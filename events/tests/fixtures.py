import pytest


@pytest.fixture
def allowed_event_configurations(event_configuration_factory):
    return event_configuration_factory.create_batch(3)


@pytest.fixture
def event_request_data(allowed_event_configurations, event_request_data_factory):
    return event_request_data_factory(allowed_event_configurations=allowed_event_configurations)
