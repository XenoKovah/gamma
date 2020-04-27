"""
Integration tests.
"""

import random
import string
import json

from django.contrib.auth.models import User
import pytest
import requests
from rest_framework import status

from achievements.models import Achievement, Event, StatusBadge
from achievements.services import AchievementRulesMongo
from core.mongo import c_badges


def test_dashboard(live_server, settings, client, rand_str):
    """
    Test dashboard page for logged user.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)

    user = User(username=rand_str, password=rand_str)
    user.save()
    client.force_login(user=user)

    res = client.get(live_server.url)
    content = res.content.decode('utf-8')
    assert 'Logout' in content
    assert 'header-nav-wrap' in content
    assert 'footer' in content


def test_dashboard_anonymous(live_server, client):
    """
    Test dashboard page for anonymous user.
    """
    res = client.get(live_server.url)
    content = res.content.decode('utf-8')
    assert 'Login' in content
    assert 'You need to authenticate in order to see you achievements' in content
    assert 'You logged in as user' not in content
    assert 'Congrants, you are in top 100! You rank is' not in content
    assert 'header-nav-wrap' in content
    assert 'footer' in content


def load_params_from_json(json_path):
    with open(json_path) as f:
        return json.load(f)


@pytest.mark.parametrize(
    "entry",
    load_params_from_json('core/tests/resources/badges_granting_rules.json'),
)
def test_badges_granting_rules(entry, live_server, admin_user, app_client, make_test_file):
    """
    Integration tests for Badges Granting due to Achievements Rules.

    For EACH item in json:
      1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "rules"
      2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "events"
      3. OUTPUT Check a badge: call '/api/v0/badges/' with "badges_result"
    """
    # `c_badges` and `rules` cleanup is absolutely necessary here
    # NOTE: consider cleaning up in all pytest's
    _cleanup_badges()

    for event, points in entry.get("actions_points", {}).items():
        Event.objects.update_or_create(
            event_type=event,
            defaults={'award': points}
        )

    for slug, points in entry.get("status_badges", {}).items():
        StatusBadge.objects.update_or_create(
            slug=slug,
            defaults={
                'title': slug, 'status_points': points,
                'badge_img': make_test_file()
            }
        )

    for achievement in entry["rules"]:
        Achievement.objects.get_or_create(
            slug=achievement["slug"],
            badge_img=make_test_file()
        )

    # 1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "rules"
    _update_rules(live_server, entry["rules"])

    # 2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "events"
    _send_events(live_server, admin_user, app_client, entry["events"])

    # 3. OUTPUT Check a badge: call '/api/v0/badges/' with "badges_result"
    _check_badges(live_server, admin_user, entry["badges_result"])


@pytest.mark.parametrize(
    "entry",
    load_params_from_json('core/tests/resources/badges_rules_change.json'),
)
def test_badgesview_rules_change(entry, live_server, admin_user, app_client, make_test_file):
    """
    Integration tests for Achievements Rules Changes and consequences.

    NOTE: test interval and frequency changes (filter changes).

    For EACH item in json:
      1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "initial_rules"
      2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "pre_change_events"
      3. OUTPUT Check a badge: call '/api/v0/badges/' with "pre_change_c_badges"
      4. INPUT Change a rule: call '/api/v0/badge-rules/' with "changed_rules"
      5. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_pre_hit_c_badges"
      6. INPUT Hit a changed rule: call '/api/v0/gamma-profile/' with "post_change_events"
      7. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_post_hit_c_badges"
    """

    # `c_badges` and `rules` cleanup is absolutely necessary here
    # NOTE: consider cleaning up in all pytest's
    _cleanup_badges()

    # Input
    initial_rules = entry["input"]["initial_rules"]
    changed_rules = entry["input"]["changed_rules"]
    pre_change_events = entry["input"]["pre_change_events"]
    post_change_events = entry["input"]["post_change_events"]
    # Output
    pre_change_c_badges = entry["output"]["pre_change_c_badges"]
    post_change_pre_hit_c_badges = entry["output"]["post_change_pre_hit_c_badges"]
    post_change_post_hit_c_badges = entry["output"]["post_change_post_hit_c_badges"]

    # Setup
    achievements_slug = set([rule['slug'] for rule in initial_rules + changed_rules])
    events = set([event["event_type"] for event in pre_change_events + post_change_events])
    for slug in achievements_slug:
        Achievement.objects.get_or_create(title=slug, slug=slug, badge_img=make_test_file())
    for event in events:
        Event.objects.get_or_create(event_type=event, award=10)

    # 1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "initial_rules"
    _update_rules(live_server, initial_rules)

    # 2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "pre_change_events"
    _send_events(live_server, admin_user, app_client, pre_change_events)

    # 3. OUTPUT Check a badge: call '/api/v0/badges/' with "pre_change_c_badges"
    _check_badges(live_server, admin_user, pre_change_c_badges)

    # 4. INPUT Change a rule: call '/api/v0/badge-rules/' with "changed_rules"
    _update_rules(live_server, changed_rules)

    # 5. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_pre_hit_c_badges"
    _check_badges(live_server, admin_user, post_change_pre_hit_c_badges)

    # 6. INPUT Hit a changed rule: call '/api/v0/gamma-profile/' with "post_change_events"
    _send_events(live_server, admin_user, app_client, post_change_events)

    # 7. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_post_hit_c_badges"
    # Ensure accrual continues even after a badge is granted
    # Ensure a new badge is granted post-change OR an old badge isn't revoked
    _check_badges(live_server, admin_user, post_change_post_hit_c_badges)


def _rand_str(string_length=10):
    """
    Generate a random string.
    """

    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(string_length))


def _cleanup_badges():
    """
    Clean up badges and rules Mongo collections.
    """

    c_badges().drop()
    conn = AchievementRulesMongo()
    conn.connect()
    conn.collection.drop()


def _send_events(live_server, admin_user, app_client, events):
    """
    Events integration test logic.

    Send event to hit a rule (or not).
    """

    for event in events:
        event_data = {
            'username': admin_user.username,
            'uid': _rand_str()
        }
        event_data.update(event)
        res = requests.put(
            live_server + '/api/v0/gamma-profile/',
            data=event_data,
            headers={
                'App-key': app_client.key,
                'App-secret': app_client.secret
            }
        )
        # NOTE: consider handling 406 (uid uniqueness constraint): re-generate uid till we get 200
        assert res.status_code == status.HTTP_200_OK


def _update_rules(live_server, rules):
    """
    Rules integration test logic.

    Update rules.
    """
    for rule in rules:
        response = requests.put(live_server + "/api/v0/badge-rules/", json=rule)
        assert response.status_code == status.HTTP_200_OK


def _check_badges(live_server, admin_user, expected_badges):
    """
    Badges integration test logic.

    With badges being checked and granted upon badges GET call.
    """
    res = requests.get(
        live_server+'/api/v0/badges/',
        params={'username': admin_user.username}
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    data_to_check = {}

    for badge_slug in data:
        data_to_check[badge_slug] = {}
        data_to_check[badge_slug]['done'] = data[badge_slug]['done']
        progress = data[badge_slug].get('progress', {})
        for event in progress:
            data_to_check[badge_slug][event] = {'count': progress[event]['count'], 'goal': progress[event]['goal']}
            # TODO checking urls?

    assert data_to_check == expected_badges
