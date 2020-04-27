import json

from django.core.cache import cache
from achievements.models import StatusBadge
import pytest

from edx_integration.api.v2.utils import get_gamma_events_list
from pointlog.utils import is_badge_rules_simplified


def load_params_from_json(json_path):
    with open(json_path) as f:
        return json.load(f)


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


@pytest.mark.parametrize(
    "entry",
    load_params_from_json('core/tests/resources/is_badge_rules_simplified_dataset.json'),
)
def test_is_badges_rules_simplified(entry, db, make_test_file):
    new_rules = entry.get('new_rules')
    old_rules = entry.get('old_rules')
    expected_result = entry.get('rules_simplified')
    for slug, points in entry.get("status_badges", {}).items():
        StatusBadge.objects.update_or_create(
            slug=slug,
            defaults={
                'title': slug, 'status_points': points,
                'badge_img': make_test_file()
            }
        )
    assert is_badge_rules_simplified(new_rules, old_rules) == expected_result
