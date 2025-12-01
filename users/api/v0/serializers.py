from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from achievements.models import Achievement
from achievements.serializers import AchievementDetailSerializer
from avatars.api.v0.serializers import AvatarSetSerializer, UserAvatarConfigSerializer
from avatars.models import AvatarSet, UserAvatarConfig
from badges.api.v0.serializers import BadgeSerializer
from badges.models import Badge
from users.models import GammaUser

from avatars.api.v0.serializers import AvatarProgressSerializer
from achievements.services.progress import AvatarProgressService


class GammaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GammaUser
        fields = ('id', 'user_uid', 'username', 'signup_source')


class UserGameProfileSerializer(serializers.Serializer):
    """
    Serializer for User Game Profile.
    """
    user_profile = serializers.SerializerMethodField()
    avatar_sets = serializers.SerializerMethodField()
    user_avatar_config = serializers.SerializerMethodField()
    system_badges = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    avatar_progress = serializers.SerializerMethodField()

    points = serializers.IntegerField()
    chart = serializers.JSONField()
    progress = serializers.JSONField()
    signup_source = serializers.CharField(allow_null=True)

    def get_user_profile(self, obj):
        """
        Retrieve or create a GammaUser based on the user_uid.
        """
        gamma_user = GammaUser.ensure_gamma_user_is_created(obj.user_uid)
        return GammaUserSerializer(gamma_user).data

    def get_avatar_sets(self, obj):
        """
        Get all current system AvatarSets.
        """
        avatar_sets = AvatarSet.objects.filter(is_draft=False).prefetch_related('avatars__rules')
        return AvatarSetSerializer(avatar_sets, many=True).data

    def get_user_avatar_config(self, obj):
        """
        Get Gamma User avatar config.
        """
        if (config := UserAvatarConfig.objects.filter(user=obj).first()):
            return UserAvatarConfigSerializer(config, context=self.context).data
        return None

    def get_system_badges(self, obj):
        """
        Get all system badges.
        """
        system_badges = Badge.objects.all().prefetch_related('rules')
        return BadgeSerializer(system_badges, many=True).data

    def get_badges(self, obj):
        """
        Get user's received avatars data.
        """
        content_type = ContentType.objects.get_for_model(Badge)
        received_user_badges = Achievement.objects.filter(
            content_type=content_type, user__user_uid=obj.user_uid
        )

        return AchievementDetailSerializer(received_user_badges, many=True).data

    def get_avatar_progress(self, obj):
        """
        Get avatar progress data.
        """
        if (config := UserAvatarConfig.objects.filter(user=obj).first()):
            service = AvatarProgressService(config)
            progress = service.calculate_progress()
            return AvatarProgressSerializer(progress).data
        return None
