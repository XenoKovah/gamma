"""
Integration tests.
"""
import random
import string
import json

import pytest
import requests
from rest_framework import status

from achievements.models import Achievement, Event, StatusBadge
from api.v0.views import USER_NOT_FOUND
from core import db


def test_dashboard(live_server, settings, admin_client, rand_str):
    """
    Test dashboard page for logged user.
    """
    res = admin_client.get(live_server.url)
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
def test_badges_granting_rules(entry, live_server, rand_str, app_client, make_test_file):
    """
    Integration tests for Badges Granting due to Achievements Rules.

    For EACH item in json:
      1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "rules"
      2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "events"
      3. OUTPUT Check a badge: call '/api/v0/badges/' with "badges_result"
    """

    user_uid = rand_str
    # `user_badges` and `rules` cleanup is absolutely necessary here
    # NOTE: consider cleaning up in all pytest's
    _cleanup_badges()

    for event, points in entry.get("actions_points", {}).items():
        _event = Event(event_type=event, title=event, award=points)
        _event.save()

    for slug, points in entry.get("status_badges", {}).items():
        _status_badge = StatusBadge(
            slug=slug,
            title=slug,
            status_points=points,
            badge_img=make_test_file())
        _status_badge.save()

    for achievement in entry["rules"]:
        _achievement = Achievement(slug=achievement["slug"], badge_img=make_test_file())
        _achievement.save()

    # 1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "rules"
    _update_rules(live_server, entry["rules"])

    # 2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "events"
    _send_events(live_server, user_uid, app_client, entry["events"])

    # 3. OUTPUT Check a badge: call '/api/v0/badges/' with "badges_result"
    _check_badges(live_server, user_uid, entry["badges_result"], app_client)


@pytest.mark.parametrize(
    "entry",
    load_params_from_json('core/tests/resources/badges_rules_change.json'),
)
def test_badgesview_rules_change(entry, live_server, rand_str, app_client, make_test_file):
    """
    Integration tests for Achievements Rules Changes and consequences.

    NOTE: test interval and frequency changes (filter changes).

    For EACH item in json:
      1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "initial_rules"
      2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "pre_change_events"
      3. OUTPUT Check a badge: call '/api/v0/badges/' with "pre_change_use_badges"
      4. INPUT Change a rule: call '/api/v0/badge-rules/' with "changed_rules"
      5. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_pre_hit_use_badges"
      6. INPUT Hit a changed rule: call '/api/v0/gamma-profile/' with "post_change_events"
      7. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_post_hit_use_badges"
    """
    user_uid = rand_str
    # `use_badges` and `rules` cleanup is absolutely necessary here
    # NOTE: consider cleaning up in all pytest's
    _cleanup_badges()

    # Input
    initial_rules = entry["input"]["initial_rules"]
    changed_rules = entry["input"]["changed_rules"]
    pre_change_events = entry["input"]["pre_change_events"]
    post_change_events = entry["input"]["post_change_events"]
    # Output
    pre_change_use_badges = entry["output"]["pre_change_use_badges"]
    post_change_pre_hit_use_badges = entry["output"]["post_change_pre_hit_use_badges"]
    post_change_post_hit_use_badges = entry["output"]["post_change_post_hit_use_badges"]

    # Setup
    achievements_slug = set([rule['slug'] for rule in initial_rules + changed_rules])
    events = set([event["event_type"] for event in pre_change_events + post_change_events])
    for slug in achievements_slug:
        achiev, _ = Achievement.objects.get_or_create(title=slug, slug=slug, badge_img=make_test_file())
        achiev.save()
    for event in events:
        ev, _ = Event.objects.get_or_create(event_type=event, title=event, award=10)
        ev.save()

    # 1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "initial_rules"
    _update_rules(live_server, initial_rules)

    # 2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "pre_change_events"
    _send_events(live_server, user_uid, app_client, pre_change_events)

    # 3. OUTPUT Check a badge: call '/api/v0/badges/' with "pre_change_use_badges"
    _check_badges(live_server, user_uid, pre_change_use_badges, app_client)

    # 4. INPUT Change a rule: call '/api/v0/badge-rules/' with "changed_rules"
    _update_rules(live_server, changed_rules)

    # 5. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_pre_hit_use_badges"
    _check_badges(live_server, user_uid, post_change_pre_hit_use_badges, app_client)

    # 6. INPUT Hit a changed rule: call '/api/v0/gamma-profile/' with "post_change_events"
    _send_events(live_server, user_uid, app_client, post_change_events)

    # 7. OUTPUT Check a badge: call '/api/v0/badges/' with "post_change_post_hit_use_badges"
    # Ensure accrual continues even after a badge is granted
    # Ensure a new badge is granted post-change OR an old badge isn't revoked
    _check_badges(live_server, user_uid, post_change_post_hit_use_badges, app_client)


def test_badge_deactivated(live_server, rand_str, app_client, make_test_file):
    """
    Test events after deactivation do not increase badge count.
    """
    # Setup
    user_uid = rand_str
    event_type = "event_for_test_badge_deactivated"
    ev, _ = Event.objects.get_or_create(event_type=event_type, title=event_type, award=10)
    ev.save()
    achievement_slug = "test_badge_deactivated"
    achiev, _ = Achievement.objects.get_or_create(title=achievement_slug, slug=achievement_slug,
                                                  badge_img=make_test_file())
    achiev.save()
    rules = [{"slug": achievement_slug, "actions": {event_type: 3}}]
    badges_status_before_deactivation = {achievement_slug: {event_type: {"count": 1}, "done": False}}
    event_to_send = [{"event_type": event_type}]

    # 1. INPUT Set up a rule: call '/api/v0/badge-rules/' with "initial_rules"
    _update_rules(live_server, rules)

    # 2. INPUT Hit a rule: call '/api/v0/gamma-profile/' with "pre_change_events"
    _send_events(live_server, user_uid, app_client, event_to_send)

    # 3. OUTPUT Check a badge: call '/api/v0/badges/' with "pre_change_use_badges"
    _check_badges(live_server, user_uid, badges_status_before_deactivation, app_client)

    # 4. Check badge deleted from relational DB is still present at mongo but it's active field is set to False
    achiev.delete()
    badge_state_after_deactivation = db.badges.read_one(achievement_slug)
    assert badge_state_after_deactivation['active'] is False

    # 5. INPUT Send events after badge deactivation
    _send_events(live_server, user_uid, app_client, event_to_send * 3)

    # 6. OUTPUT Check badge state after deactivation is not changed for user
    _check_badges(live_server, user_uid, badges_status_before_deactivation, app_client)


@pytest.mark.parametrize(
    "entry",
    load_params_from_json('core/tests/resources/leaderboard_cases.json'),
)
def test_leaderboard_api(entry, live_server, app_client, mocker):
    """
    Test Leaderboard API endpoint.

    Notes:
    - We'll be working with 3 users in every test case.
    - In the input file, users are be referred to by their ids we agree on: 1, 2, and 3.
    - We grant all users with same badges for the sake of simplicity. Points will differ though.
    - Output badges should be the same as input badges.

    Cases:
    1. Definite leader, all users with points.
    2. A tie for first place, all users with points.
    3. All users without points.
    4. Definite leader, other users don't have points.
    5. The user of interest (whose username is in params) doesn't have points; still present in the leaderboard, rank is affected.
    6. The user of interest (whose username is in params) is not found. Other users' stats won't show up.
    7. The user of interest (whose username is in params) isn't present in db when we make a request. We still get the leaderboard. Only users, created BEFORE the call, appear in the rating.
    8. Username param is absent in a request. It's OK.
    """

    # Consts that need to match with the input data.
    USERNAME_PATTERN = "user{!s}"
    # It's important use 1-based users numeration (see the docstring).
    USERS_VERBOSE_NUMERATION_START = 1
    USERS_VERBOSE_NUMERATION_STOP = 4

    _cleanup_badges()

    users_points = entry["input"].get("users_points", {})
    # User whose username will be passed as a param
    user_uid = entry["input"].get("user_uid")
    badges = entry["input"].get("badges")
    output_rank = entry["output"].get("rank")
    output_sorted_users = entry["output"].get("users_sorting_by_points")
    output_status_code = entry["output"].get("status_code")
    # Users number in the leaderboard
    output_users_number = entry["output"].get("returned_users_number")

    # Set up users and their badges
    for i in range(USERS_VERBOSE_NUMERATION_START, USERS_VERBOSE_NUMERATION_STOP):
        username = USERNAME_PATTERN.format(i)

        with db.users.read_and_update(username) as user:
            user.username = username
            user.points = users_points.get(str(i), {}).get("points")
            user.badges = badges

    if output_status_code == status.HTTP_404_NOT_FOUND:
        mocked = mocker.patch("api.v0.views.db.users.read_one")
        mocked.return_value = None

    headers = {
        'Content-Type': 'application/json',
        'App-key': app_client.key,
        'App-secret': app_client.secret,
    }
    resp = requests.get(
        live_server + "/api/v0/leaderboard/",
        params={'username': USERNAME_PATTERN.format(user_uid)},
        headers=headers,
    )

    assert resp.status_code == output_status_code

    resp_body = resp.json()

    if resp.status_code == status.HTTP_200_OK:
        gameprofiles = resp_body["gameprofiles"]

        assert len(resp_body["gameprofiles"]) == output_users_number
        # Ensure a rank of a user of interest is as expected
        assert resp_body.get("rank") == output_rank

        # Switching to a 0-based users numeration.
        for i in range(USERS_VERBOSE_NUMERATION_STOP - 1):
            # Check `gameprofiles` fields nomenclature
            assert "username" in gameprofiles[i]
            assert "user_uid" in gameprofiles[i]
            assert "points" in gameprofiles[i]
            assert "badges" in gameprofiles[i]

            # Test 'username' value
            assert gameprofiles[i]["username"] == USERNAME_PATTERN.format(output_sorted_users[i])

            # Test 'points' value.
            for j, el in enumerate(gameprofiles):
                if str(output_sorted_users[i]) in gameprofiles[j]["user_uid"]:
                    # Had to lookup particular user's points in expected values
                    assert gameprofiles[j]["points"] == users_points[str(output_sorted_users[i])]["points"]
                    break

            # Test sorting by points by checking user id membership: user_uid` has numeric id in it
            # Test 'user_uid' value as well
            assert str(output_sorted_users[i]) in gameprofiles[i]["user_uid"]

            # Check badges data. Checking the first badge only.
            # Check badge uuid
            assert "badge_1" in gameprofiles[i]["badges"]
            response_badges_data = gameprofiles[i]["badges"]["badge_1"]
            expected_badges_data = badges["badge_1"]

            if badges.get('badge_false'):
                assert "badge_false" not in gameprofiles[i]["badges"]

            # Key defined in the input data
            response_badge_progress_data = response_badges_data["progress"]["edx_cert_created"]
            expected_badge_progress_data = expected_badges_data["progress"]["edx_cert_created"]
            assert expected_badges_data["done"] == response_badges_data["done"]
            assert expected_badges_data["url"] == response_badges_data["url"]
            assert expected_badge_progress_data["count"] == response_badge_progress_data["count"]
            assert expected_badge_progress_data["goal"] == response_badge_progress_data["goal"]

    elif resp.status_code == status.HTTP_404_NOT_FOUND:
        assert resp_body.get("Error") == USER_NOT_FOUND
        assert "gameprofiles" not in resp_body
        assert "rank" not in resp_body

    else:
        raise NotImplementedError(
            "Tests for the cases with other status codes are not implemented."
        )


def _create_badges(user_uid, badges, badge_uid, upsert=True):
    """
    Insert badges as ready-made docs instead of using API.
    """
    for badge in badges:
        badge_data = list(badge.values())[0]
        db.users.update_badge(
            user_uid,
            badge_uid=badge_uid,
            badge_url=badge_data["url"],
            progress=badge_data["progress"],
            done=badge_data["done"],
            upsert=upsert,
        )


def _cleanup_badges():
    """
    Clean up badges and rules Mongo collections.
    """

    db.engine.conn.db.users.drop()
    db.engine.conn.db.badges.drop()
    db.engine.conn.db.statuses.drop()
    db.engine.conn.db.events.drop()
    db.engine.conn.db.event_history.drop()


def _rand_str(string_length=10):
    """
    Generate a random string.
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(string_length))


def _send_events(live_server, user_uid, app_client, events):
    """
    Events integration test logic.

    Send event to hit a rule (or not).
    """

    for event in events:
        event_data = {
            'username': user_uid,
            'uid': _rand_str(),
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


def _check_badges(live_server, user_uid, expected_badges, app_client):
    """
    Badges integration test logic.
    """
    res = requests.get(
        live_server + '/api/v0/gamma-profile/',
        params={'username': user_uid},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    user_badges = data["badges"]

    data_to_check = {}

    for badge_slug in user_badges:
        data_to_check[badge_slug] = {}
        data_to_check[badge_slug]['done'] = user_badges[badge_slug]['done']
        progress = user_badges[badge_slug].get('progress', {})
        for event in progress:
            data_to_check[badge_slug][event] = {'count': progress[event]['count']}
            # NOTE: consider checking urls

    assert data_to_check == expected_badges
