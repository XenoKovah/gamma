import pytest  # pylint: disable=import-error

from core import db
from core.tests.utils.helpers import load_params_from_json


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
