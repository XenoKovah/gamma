from rest_framework import serializers

from achievements.models import Achievement
from badges.utils import is_achieved_badge
from users.models import GammaUser


class LeaderboardMemberBadgeSerializer(serializers.ModelSerializer):
    """
    Serialize a user badge data required for displaying on a leaderboard.
    """

    progress = serializers.JSONField(source="achievement_dependencies")
    url = serializers.SerializerMethodField()

    def get_url(self, obj: Achievement) -> str:
        """
        Provide the badge image URL.
        """
        return obj.content_object.image.url

    class Meta:
        model = Achievement
        fields = ("title", "description", "progress", "url")


class LeaderboardMemberSerializer(serializers.ModelSerializer):
    """
    Serialize a user data required for displaying on a leaderboard.
    """

    badges = serializers.SerializerMethodField()

    def get_badges(self, obj: GammaUser) -> dict:
        """
        Provide a leaderboard-related badges achieved by a user.

        If there is a course_id in the context, only course-related badges
        are returned.
        """
        course_id = self.context["leaderboard_retrieving_context"].course_id
        achieved_badges = [
            achievement for achievement in obj.achievement_set.all()
            if is_achieved_badge(achievement, course_id)
        ]
        return LeaderboardMemberBadgeSerializer(achieved_badges, many=True, read_only=True).data

    class Meta:
        model = GammaUser
        fields = ("user_uid", "signup_source", "badges")
