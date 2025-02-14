import pytest


@pytest.fixture
def mock_gamification_backends(mocker):
    mock_backends = mocker.patch('rules.signals.get_gamification_backends')
    mock_backend = mocker.MagicMock()
    mock_backend.NAME = 'badge'
    mock_backends.return_value = [mock_backend]
    yield mock_backend


@pytest.fixture
def mock_rules_filter(mocker):
    mock_filter = mocker.patch('rules.signals.RulesFilterService')
    mock_instance = mock_filter.return_value
    yield mock_instance
