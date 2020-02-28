from django.core.cache import cache

from edx_integration.api.v2.utils import get_gamma_events_list


def test_get_gamma_events_list_from_cache(monkeypatch):
    cached_value = [
        {
            "verbose_name": "Test Event 1",
            "event_type": "test1event"
        },
        {
            "verbose_name": "Test Event 2",
            "event_type": "test2event"
        }
    ]

    def mock_cache_get(*args, **kwargs):
        return cached_value

    monkeypatch.setattr(
        cache,
        'get',
        mock_cache_get
    )

    res = get_gamma_events_list()
    assert res == cached_value
