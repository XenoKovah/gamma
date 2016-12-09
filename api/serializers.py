from rest_framework import serializers

from core.models import GameProfile, Event
from achievements.models import Achievement
from pointlog.models import LoggedEvent, ApiAccessEvent


class GameProfileSerializer(serializers.ModelSerializer):
    """
    GameProfile Model Serializer.
    """
    class Meta:
        model = GameProfile
        fields = ('points',)


class ProgressSerializer(serializers.Serializer):
    """
    Progress serializer.
    """
    date = serializers.DateTimeField()
    points = serializers.IntegerField()


class BadgesSerializer(serializers.ModelSerializer):
    """
    Achievement serializer.

    Returns:
      - url: absolute URL for Badge Image
      - title: Badge title
      - slug: Badge slug (unique across DB)
      - description: Badge description
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = (
            'url',
            'title',
            'slug',
            'description',
            'status_badge',
            'status_points',
            'status_color'
        )

    def get_url(self, obj):
        if obj.badge_img:
            return self.context['request'].build_absolute_uri(obj.badge_img.url)


class LoggedEventSerializer(serializers.ModelSerializer):
    """
    EventLogged model serializer.
    """
    color = serializers.SerializerMethodField()

    class Meta:
        model = LoggedEvent

    def get_color(self, obj):
        """
        Return Event color.
        """
        color = Event.objects.values_list('color').get(event_type=obj.event_type)
        return color[0]-1 if color else None


class ApiAccessEventSerializer(serializers.ModelSerializer):
    """
    EventLogged model serializer.
    """
    class Meta:
        model = ApiAccessEvent
