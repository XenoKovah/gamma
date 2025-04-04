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

    class Meta:
        model = Achievement
        fields = ('title', 'slug', 'description', 'done', 'progress', 'object_id', 'object_uri', 'is_active')

    def get_slug(self, obj):
        """
        Get the achievement slug.
        """
        if isinstance(obj.content_object, Badge):
            return obj.content_object.slug
        return None

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
