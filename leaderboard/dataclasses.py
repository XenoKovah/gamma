from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from django.conf import settings

from leaderboard.constants import COURSE_LEADERBOARD_ID_TEMPLATE, GENERAL_LEADERBOARD_ID_TEMPLATE


@dataclass
class LeaderboardRetrievingContext:
    """
    Encapsulate data related to the personalized leaderboard retrieving.
    """

    user_uid: Optional[str]
    user_signup_source: Optional[str]
    course_id: Optional[str]

    @cached_property
    def leaderboard_id(self) -> str:
        """
        Provide a leaderboard ID based on the context data.
        """
        user_signup_source = self.user_signup_source or settings.MAIN_SIGNUP_SOURCE
        course_id = self.course_id

        return (
            COURSE_LEADERBOARD_ID_TEMPLATE.format(user_signup_source=user_signup_source, course_id=course_id)
            if course_id
            else GENERAL_LEADERBOARD_ID_TEMPLATE.format(user_signup_source=user_signup_source)
        )
