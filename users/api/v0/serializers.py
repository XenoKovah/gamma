from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from achievements.models import Achievement
from achievements.serializers import AchievementDetailSerializer
from avatars.api.v0.serializers import AvatarSetSerializer, UserAvatarConfigSerializer
from avatars.models import AvatarSet, UserAvatarConfig
from badges.api.v0.serializers import BadgeSerializer
from badges.models import Badge
from users.models import GammaUser


class GammaUserInfoSerializer(serializers.Serializer):
    """
    Serializer for GammaUser information.
    """

    gamma_user_id = serializers.SerializerMethodField()
    user_avatar_config = serializers.SerializerMethodField()

    def get_gamma_user_id(self, obj):
        """
        Get Gamma User ID.
        """
        gamma_user = GammaUser.ensure_gamma_user_is_created(self.context.get('user_uid'))

        return gamma_user.id

    def get_user_avatar_config(self, obj):
        """
        Get Gamma User Avatar Set info.
        """
        gamma_user = GammaUser.ensure_gamma_user_is_created(self.context.get('user_uid'))
        user_avatar_set = UserAvatarConfig.objects.filter(user_id=gamma_user.id).first()
        user_avatar_config = UserAvatarConfigSerializer(user_avatar_set).data if user_avatar_set else None

        return user_avatar_config


class UserGameProfileSerializer(serializers.Serializer):
    """
    Serializer for User Game Profile.
    """

    avatar_sets = serializers.SerializerMethodField()
    gamma_user_info = serializers.SerializerMethodField()
    system_badges = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()

    def get_avatar_sets(self, obj):
        """
        Get all current system AvatarSets.
        """
        avatar_sets = AvatarSet.objects.filter(is_draft=False).prefetch_related('avatars__rules')
        return AvatarSetSerializer(avatar_sets, many=True).data

    def get_gamma_user_info(self, obj):
        """
        Get Gamma User profile info.
        """
        user_uid = self.context.get('user_uid')
        return GammaUserInfoSerializer(obj, context={'user_uid': user_uid}).data

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
            content_type=content_type, user__user_uid=self.context.get('user_uid')
        )

        return AchievementDetailSerializer(received_user_badges, many=True).data
