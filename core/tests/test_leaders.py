import pytest  # pylint: disable=import-error

from core import db
from core.db.leaders import get_top10, get_tail_competitors
from core.tests.utils.helpers import load_params_from_json


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "entry",
    load_params_from_json("core/tests/resources/personalized_leaderboard_cases.json")
)
def test_read_for_user(entry):
    """
    Test the function responsible for retrieving the required dataset from
    the MongoDB database to construct the leaderboard.
    """
    user_uid = entry["user_uid"]
    user_signup_source = entry["signup_source"]
    expected_top10 = entry["expected_top10"]
    expected_competitors = entry["expected_competitors"]
    expected_rank = entry["expected_rank"]

    db.engine.conn.db.users.drop()

    for i in range(1, 31):
        with db.users.read_and_update(f"user_uid_{i}") as user:
            user.signup_source = user_signup_source
            user.points = 31-i

    leaders, competitors, rank = db.leaders.read_for_user(user_uid, user_signup_source)
    
    top10 = leaders.to_primitive("roster").get("roster")
    competitors = competitors.to_primitive("roster").get("roster") if competitors else []

    assert expected_rank == rank
    assert expected_top10 == top10
    assert expected_competitors == competitors


@pytest.mark.parametrize(
    "entry",
    load_params_from_json("core/tests/resources/leaderboard_with_signup_source_cases.json")
)
def test_read_for_user_according_to_signup_source(entry):
    """
    Test the function responsible for retrieving the required dataset from
    the MongoDB database to build the leaderboard filtered by signup_source.
    """
    user_uid = entry["user_uid"]
    signup_source = entry["signup_source"]
    expected_top10 = entry["expected_top10"]
    expected_competitors = entry["expected_competitors"]
    expected_rank = entry["expected_rank"]

    db.engine.conn.db.users.drop()

    # Odd users are created with signup_source = "RG", even - signup_source = "main"
    for i in range(1, 31):
        with db.users.read_and_update(f"user_uid_{i}") as user:
            if i % 2 == 0:
                user.signup_source = signup_source[i % 2]
            else:
                user.signup_source = signup_source[i % 2]
            user.points = 31 - i

    leaders, competitors, rank = db.leaders.read_for_user(user_uid, signup_source[1])
    top10 = leaders.to_primitive("roster").get("roster")
    competitors = competitors.to_primitive("roster").get("roster") if competitors else []

    assert expected_rank == rank
    assert expected_top10 == top10
    assert expected_competitors == competitors


@pytest.mark.parametrize(
    "entry",
    load_params_from_json("core/tests/resources/leaderboard_cases_with_same_points.json")
)
def test_read_for_user_with_same_points(entry, mocker):
    """
    A test for all cases where users have the same points.
    """
    all_users = entry["all_users"]
    user_uid = entry["user_uid"]
    signup_source = entry["signup_source"]
    tail = entry["tail"]
    head = entry["head"]
    expected_top10 = entry["expected_top10"]
    expected_competitors = entry["expected_competitors"]
    expected_rank = entry["expected_rank"]

    db.engine.conn.db.users.drop()

    for item in all_users:
        with db.users.read_and_update(item["user_uid"]) as user:
            user.signup_source = signup_source
            user.points = item["points"]

    mocked_get = mocker.patch('core.db.leaders.get_tenant_filter')
    mocked_get.return_value = { "signup_source": f"{signup_source}" }

    mocked_get = mocker.patch('core.db.leaders.get_user_rank')
    mocked_get.return_value = expected_rank

    mocked_get = mocker.patch('core.db.leaders.get_top10')
    mocked_get.return_value = expected_top10

    mocked_get = mocker.patch('core.db.leaders.get_tail_competitors')
    mocked_get.return_value = tail

    mocked_get = mocker.patch('core.db.leaders.get_head_competitors')
    mocked_get.return_value = head

    top10, competitors, rank = db.leaders.read_for_user(user_uid, signup_source)
    competitors = competitors.to_primitive("roster").get("roster") if competitors else []

    assert expected_rank == rank
    assert expected_top10 == top10
    assert expected_competitors == competitors


def test_get_incomplete_top10_when_current_user_has_no_points():
    """
    Test, when there are less than 10 total users with points and the current user, has no points.
    """
    db.engine.conn.db.users.drop()

    for item in range(1, 3):
        with db.users.read_and_update(f"user_uid_{item}") as user:
            user.points = 3 - item

    current_user = db.users.read_one("current_user")
    rank = 3
    additional_filter = {}

    expected_top10 = get_top10(current_user, rank, additional_filter)

    assert len(expected_top10.to_primitive('roster').get('roster')) == 2
    assert expected_top10.to_primitive('roster').get('roster')[0]["user_uid"] == "user_uid_1"
    assert expected_top10.to_primitive('roster').get('roster')[1]["user_uid"] == "user_uid_2"


def test_get_top10_when_current_user_has_rank_10():
    """
    Test when the total number of users with scores is 9 and the current user has a rank of 10.
    """
    db.engine.conn.db.users.drop()

    for item in range(1, 10):
        with db.users.read_and_update(f"user_uid_{item}") as user:
            user.points = 11 - item 

    current_user = db.users.read_one("current_user")
    current_user.points = 1
    rank = 10
    additional_filter = {}

    expected_top10 = get_top10(current_user, rank, additional_filter)

    assert len(expected_top10.to_primitive('roster').get('roster')) == 10
    assert expected_top10.to_primitive('roster').get('roster')[9]["user_uid"] == "current_user"


def test_get_empty_top10():
    """
    Test when there are no users with points.
    """
    db.engine.conn.db.users.drop()

    current_user = db.users.read_one("current_user")
    current_user.points = 0
    rank = 1
    additional_filter = {}

    expected_top10 = get_top10(current_user, rank, additional_filter)

    assert len(expected_top10.to_primitive('roster').get('roster')) == 0


@pytest.mark.parametrize(
    "entry",
    load_params_from_json("core/tests/resources/cases_tail_competitors.json")
)
def test_get_tail_competitors(entry):
    """
    Test, the get_tail_competitors function returns the correct number of users.
    """
    points = entry["points"]
    expected_length = entry["expected_length"]

    db.engine.conn.db.users.drop()

    for item in range(30):
        with db.users.read_and_update(f"user_uid_{item}") as user:
            user.points = 31 - item 

    current_user = db.users.read_one("current_user")
    current_user.points = points
    additional_filter = {}

    tail = get_tail_competitors(current_user, additional_filter)

    assert len(tail) == expected_length
