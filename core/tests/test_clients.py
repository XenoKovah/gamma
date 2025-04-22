import pytest

from core import db
from core.data_models.models import AppClient


pytestmark = pytest.mark.django_db


def test_app_client_rewrite():
    """
    Test correct rewrite of the AppClient document.
    """
    uid = "uid_test1"
    original_key, original_secret = "key1", "secret1"
    new_key, new_secret = "key2", "secret2"

    db.clients.update_one(AppClient({
        "uid": uid,
        "key": original_key,
        "secret": original_secret}))

    db.clients.update_one(AppClient({
        "uid": uid,
        "key": new_key,
        "secret": new_secret}))

    client = db.clients.read_one(key=new_key, secret=new_secret)

    assert client.key == new_key
    assert client.secret == new_secret
    assert client.uid == uid


def test_app_client_new_creation():
    """""
    Create two separate AppClient documents.
    """
    uid1, uid2 = "uid_test1", "uid_test2"
    key1, secret1 = "key1", "secret1"
    key2, secret2 = "key2", "secret2"

    db.clients.update_one(AppClient({
        "uid": uid1,
        "key": key1,
        "secret": secret1}))

    db.clients.update_one(AppClient({
        "uid": uid2,
        "key": key2,
        "secret": secret2}))

    client1 = db.clients.read_one(key=key1, secret=secret1)
    client2 = db.clients.read_one(key=key2, secret=secret2)

    assert client1.key == key1
    assert client1.secret == secret1
    assert client1.uid == uid1

    assert client2.key == key2
    assert client2.secret == secret2
    assert client2.uid == uid2
