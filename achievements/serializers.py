from rest_framework import serializers

from achievements.models import Achievement, AchievementRule


class AchievementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for receiving achievement details.
    """

    done = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    object_uri = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ('title', 'description', 'done', 'progress', 'object_id', 'object_uri')

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
