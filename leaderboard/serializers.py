from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from achievements.models import Achievement, AchievementRule
from badges.models import Badge
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
        badge_content_type = ContentType.objects.get_for_model(Badge)
        achieved_badges = [
            achievement for achievement in obj.achievement_set.all()
            if achievement.content_type == badge_content_type and achievement.all_rules_completed
        ]
        return LeaderboardMemberBadgeSerializer(achieved_badges, many=True, read_only=True).data

    class Meta:
        model = GammaUser
        fields = ("user_uid", "signup_source", "badges")
