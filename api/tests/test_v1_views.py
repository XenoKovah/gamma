import pytest  # pylint: disable=import-error
import requests

from django.urls import reverse
from rest_framework import status

from core import db
from core.tests.utils.helpers import load_params_from_json


@pytest.mark.parametrize(
    "entry",
    load_params_from_json("api/tests/resources/leaderboard_view_cases.json")
)
def test_API_for_leaderboard_data(live_server, entry):
    """
    API test to check returned leaderboard data (API v1).
    """
    db.engine.conn.db.users.drop()
    db.engine.conn.db.statuses.drop()

    user_uid = entry["user_uid"]
    user_signup_source = entry["user_signup_source"]
    expected_data = entry["expected_data"]

    url = (
        live_server + 
        reverse("api:v1:leaderboard").rstrip("/") + 
        f"?username={user_uid}&signup_source={user_signup_source}"
    )

    signup_source = ["main", "RG"]
    # Creating Users in Mongo DB
    # Odd users are created with signup_source = "RG", even - signup_source = "main"
    for i in range(1, 31):
        with db.users.read_and_update(f"user_uid_{i}") as user:
            if i % 2 == 0:
                user.signup_source = signup_source[i % 2]
            else:
                user.signup_source = signup_source[i % 2]
            user.points = 31 - i

    response = requests.get(
        url,
        headers={
            "App-key": "key",
            "App-secret": "secret",
        },
        verify=False
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_data
