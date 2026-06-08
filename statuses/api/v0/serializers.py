from rest_framework import serializers

from statuses.models import Status


class SystemStatusSerializer(serializers.ModelSerializer):
    """
    Read-only serializer shaping a Status into the exact payload the learner
    dashboard's "Your Statuses" block expects.

    The field names ``url`` / ``status_uid`` / ``active`` intentionally match the
    frontend contract in edx-gamma-dashboard (``mapStatusItems`` ->
    ``SliderStatusesBlock``); do not rename them without updating that consumer.
    """

    url = serializers.ImageField(source='image', read_only=True)
    status_uid = serializers.CharField(source='slug', read_only=True)
    active = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = Status
        fields = ('status_points', 'title', 'color', 'url', 'status_uid', 'active', 'slug')
