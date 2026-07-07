from rest_framework import serializers

from achievements.models import Achievement
from badges.models import Badge
from badges.utils import is_achieved_badge
from users.models import GammaUser


class LeaderboardMemberBadgeSerializer(serializers.ModelSerializer):
    """
    Serialize a user badge data required for displaying on a leaderboard.
    """

    progress = serializers.JSONField(source="achievement_dependencies")
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    def get_title(self, obj: Achievement) -> str:
        """
        Provide the badge's *current* title, falling back to the achievement's
        award-time snapshot. Reading through ``content_object`` means renaming a
        badge is reflected on the leaderboard immediately, instead of showing the
        stale name copied onto the achievement when it was earned.
        """
        badge = obj.content_object
        if isinstance(badge, Badge) and badge.title:
            return badge.title
        return obj.title

    def get_description(self, obj: Achievement) -> str:
        """
        Provide the badge's *current* description, falling back to the achievement
        snapshot (mirrors ``get_title``).
        """
        badge = obj.content_object
        if isinstance(badge, Badge) and badge.description:
            return badge.description
        return obj.description or ""

    def get_url(self, obj: Achievement) -> str:
        """
        Provide the badge image URL. Defensive against a dangling badge (the
        Badge was deleted but the Achievement remains) — get_badges already
        filters those out, but never crash the whole leaderboard on one bad row.
        """
        image = getattr(obj.content_object, "image", None)
        return image.url if image else None

    def get_slug(self, obj: Achievement) -> str:
        """
        Provide the badge slug so the dashboard can link each leaderboard icon
        to its per-badge leaderboard. Defensive against a dangling badge.
        """
        return getattr(obj.content_object, "slug", None)

    class Meta:
        model = Achievement
        fields = ("title", "slug", "description", "progress", "url")


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
            # Exclude dangling achievements whose Badge was deleted: they can't be
            # rendered (no image/slug/title) and would otherwise crash the whole
            # leaderboard response when this member is serialized.
            if is_achieved_badge(achievement, course_id) and achievement.content_object is not None
        ]
        # Show the highest-value badges first: order by the badge's completion
        # points (Badge.points), descending. Python's sort is stable, so badges
        # tied on points keep their existing order. getattr guards a dangling
        # badge whose content_object no longer resolves.
        achieved_badges.sort(
            key=lambda achievement: getattr(achievement.content_object, "points", 0) or 0,
            reverse=True,
        )
        return LeaderboardMemberBadgeSerializer(achieved_badges, many=True, read_only=True).data

    class Meta:
        model = GammaUser
        fields = ("user_uid", "signup_source", "badges")
