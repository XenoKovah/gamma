import pytest
from schematics.exceptions import DataError

from core.notif.models import OneSignalNotif as Notif


@pytest.mark.xfail(raises=DataError)
@pytest.mark.unittests
def test_use_user_ids_with_player_ids():
    Notif({
        "headings": {"en": "Heading"},
        "contents": {"en": "Contents"},
        "include_external_user_ids": ["username1"],
        "include_player_ids": ["player_id_1"]
    }).validate()


@pytest.mark.unittests
def test_direct_model():
    notif = Notif()
    data = notif.to_native("public")

    assert "_id" not in data
