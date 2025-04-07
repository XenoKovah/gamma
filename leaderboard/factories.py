import factory

from leaderboard.dataclasses import LeaderboardRetrievingContext


class LeaderboardRetrievingContextFactory(factory.Factory):
    """
    Factory for creating LeaderboardRetrievingContext instances.
    """

    user_uid = factory.Faker("uuid4")
    user_signup_source = "main"
    course_id = None

    class Meta:
        model = LeaderboardRetrievingContext
