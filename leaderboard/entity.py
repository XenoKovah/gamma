from schematics.models import Model
from schematics.types import IntType, StringType


class LeaderboardMember(Model):
    """
    Encapsulate the data about a user in the leaderboard.
    """

    user_uid = StringType(required=True)
    points = IntType(required=True)

    def __str__(self) -> str:
        return f"{self.user_uid} ({self.points} points)"

    def __repr__(self) -> str:
        return f'LeaderboardMember({{"user_uid": "{self.user_uid}", "points": {self.points}}})'


class UserLeaderboardsData(Model):
    """
    Encapsulate user data required for leaderboards building.
    """

    user_uid = StringType(required=True)
    points = IntType(required=True)
    signup_source = StringType(required=True, serialize_when_none=True)
