from rest_framework import serializers

from achievements.models import Achievement
from badges.models import Badge


class AchievementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for receiving achievement details.
    """

    done = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    object_uri = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ('title', 'slug', 'description', 'done', 'progress', 'object_id', 'object_uri', 'is_active', 'points')

    def get_slug(self, obj):
        """
        Get the achievement slug.
        """
        if isinstance(obj.content_object, Badge):
            return obj.content_object.slug
        return None

    def get_points(self, obj):
        """
        Completion points configured on the badge ("Points for completion" on the
        dashboard). 0 for non-badge achievements or unset/dangling badges.
        """
        if isinstance(obj.content_object, Badge):
            return obj.content_object.points
        return 0

    def get_is_active(self, obj):
        """
        Get the achievement active status.
        """
        if isinstance(obj.content_object, Badge):
            return obj.content_object.is_active
        return None

    def get_done(self, obj):
        """
        Get the achievement completion status.
        """
        return obj.all_rules_completed

    def get_progress(self, obj):
        """
        Get the achievement progress details.
        """
        return obj.achievement_dependencies

    def get_object_uri(self, obj):
        """
        Get the image URI if available.
        """
        object_uri = getattr(obj.content_object, 'image', None)
        return object_uri.url if object_uri else None


class BadgeNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for a pending "badge earned" notification.

    Prefers the badge's current title/description/image over the snapshot stored
    on the achievement at award time, so notifications always show the up-to-date
    badge configuration. The image is a media-relative URL; the LMS-side consumer
    absolutizes it against the public Gamma base URL.
    """

    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ('uuid', 'slug', 'title', 'description', 'image', 'completed_at')

    def get_slug(self, obj):
        """
        Get the badge slug.
        """
        if isinstance(obj.content_object, Badge):
            return obj.content_object.slug
        return None

    def get_title(self, obj):
        """
        Get the badge's current title, falling back to the achievement snapshot.
        """
        if isinstance(obj.content_object, Badge) and obj.content_object.title:
            return obj.content_object.title
        return obj.title

    def get_description(self, obj):
        """
        Get the badge's current description, falling back to the achievement snapshot.
        """
        if isinstance(obj.content_object, Badge) and obj.content_object.description:
            return obj.content_object.description
        return obj.description or ''

    def get_image(self, obj):
        """
        Get the badge image URI if available.
        """
        image = getattr(obj.content_object, 'image', None)
        return image.url if image else None
