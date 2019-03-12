from rest_framework import serializers

from core.models import GameProfile
from achievements.models import Achievement, Event, StatusBadge
from pointlog.models import LoggedEvent, ApiAccessEvent


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

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
        )

    def get_url(self, obj):
        if obj.badge_img:
            return self.context['request'].build_absolute_uri(obj.badge_img.url)


class UserStatusSerializer(serializers.ModelSerializer):
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
        model = StatusBadge
        fields = (
            'url',
            'title',
            'slug',
            'description',
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
    msg = serializers.SerializerMethodField()

    class Meta:
        model = LoggedEvent
        fields = '__all__'

    def get_color(self, obj):
        """
        Return Event color.
        """
        if not hasattr(obj, 'related_event'):
            obj.event = Event.objects.get(event_type=obj.event_type)
        return obj.event.color - 1

    def get_msg(self, obj):
        if not hasattr(obj, 'related_event'):
            obj.related_event = Event.objects.get(event_type=obj.event_type)
        return obj.event.notification_message.format(obj.rewarded_points)


class ApiAccessEventSerializer(serializers.ModelSerializer):
    """
    EventLogged model serializer.
    """
    class Meta:
        model = ApiAccessEvent


class EventSerializer(serializers.ModelSerializer):
    """
    Event model serializer.
    """
    class Meta:
        model = Event
        fields = ('event_type',)
