import json
import requests

from core import db
from core.data_models.models import User
from django.urls import reverse
from rest_framework import status


def test_update_profile_signup_source(live_server):
    """
    API test for updating game profiles with registration source data.
    """
    url = live_server + reverse("api:v0:update-profile-signup-source")
    db.engine.conn.db.users.drop()
    data = {
        "tenant": "test-site.com",
        "uids": [
            "username1",
            "username2",
            "username3",
        ]
    }
    db.users.create(User({"user_uid": "username1"}))

    response = requests.post(
        url,
        json=json.dumps(data),
        headers={
            "App-key": "key",
            "App-secret": "secret",
        },
        verify=False
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"count": 1}
