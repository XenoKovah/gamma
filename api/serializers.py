import random
from rest_framework import serializers

from core.models import GameProfile
from achievements.models import Achievement, Event, StatusBadge
from pointlog.models import LoggedEvent, ApiAccessEvent
from django.contrib.auth.models import User
from core.mongo import c_badges


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class GameProfileSerializer(serializers.ModelSerializer):
    """
    GameProfile Model Serializer.
    """
    user = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    goal = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()

    class Meta:
        model = GameProfile
        fields = ('points', 'user', 'progress', 'goal', 'avatar', 'position', 'badges')

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    def get_progress(self, obj):
        return random.randint(0,50)

    def get_goal(self, obj):
        return 100

    def get_badges(self, obj):
        user_badges = c_badges().find_one({"user_id": obj.user.id}) or {}

        # TODO: in case of changed deployment arch need to build absolute url based on public domain name
        request = self.context.get('request')
        return [request.build_absolute_uri(user_badges.get('badges', {}).get(badge, {}).get('url')) for
            badge in user_badges.get('badges', {}) if user_badges.get('badges', {}).get(badge, {}).get('done')]


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

class StatusSerializer(serializers.ModelSerializer):
    """
    Achievement serializer.

    Returns:
      - url: absolute URL for Badge Image
      - title: Badge title
      - slug: Badge slug (unique across DB)
      - description: Badge description
      - done: ir finish status True else False
      - progress: student status progress

    """
    url = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    done = serializers.SerializerMethodField()

    class Meta:
        model = StatusBadge
        fields = (
            'url',
            'title',
            'slug',
            'description',
            'status_points',
            'status_color',
            'progress',
            'done'
        )

    def get_url(self, obj):
        if obj.badge_img:
            return self.context['request'].build_absolute_uri(obj.badge_img.url)

    def get_progress(self, obj):
        return self.context['progress']

    def get_done(self, obj):
        if obj.status_points / self.context['progress'] <= 1:
            return True
        else :
            return False

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
