from rest_framework import serializers

from .models import GameProfile


class GameProfileSerializer(serializers.ModelSerializer):
    """
    GameProfile Model Serializer.
    """
    class Meta:
        model = GameProfile


class ProgressSerializer(serializers.Serializer):
    """
    Progress serializer.
    """
    date = serializers.DateTimeField()
    points = serializers.IntegerField()
