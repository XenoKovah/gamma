from rest_framework import serializers

from avatars.models import AvatarSet, UserAvatarConfig
from users.models import GammaUser
from avatars.api.v0.serializers import AvatarSetSerializer, UserAvatarConfigSerializer


class GammaUserInfoSerializer(serializers.Serializer):
    """
    Serializer for GammaUser information.
    """
    gamma_user_id = serializers.IntegerField()
    user_avatar_set_info = UserAvatarConfigSerializer(allow_null=True)

    @staticmethod
    def get_gamma_user_info(user_uid):
        """
        Get `GammaUser` ID and `UserAvatarConfig` data.
        """
        gamma_user, __ = GammaUser.objects.get_or_create(user_uid=user_uid)
        user_avatar_set = UserAvatarConfig.objects.filter(user_id=gamma_user.id).first()
        user_avatar_set_info = UserAvatarConfigSerializer(user_avatar_set).data if user_avatar_set else None

        return {
            'gamma_user_id': gamma_user.id,
            'user_avatar_set_info': user_avatar_set_info,
        }


class UserGameProfileSerializer(serializers.Serializer):
    """
    Serializer for User Game Profile.
    """

    avatar_sets = AvatarSetSerializer(many=True, read_only=True)
    gamma_user_info = GammaUserInfoSerializer(read_only=True)

    def to_representation(self, instance):
        """
        Override to_representation to fetch additional fields dynamically.
        """
        data = super().to_representation(instance)

        avatar_sets = AvatarSet.objects.all().prefetch_related('avatars__rules')
        user_uid = self.context.get('user_uid')

        data['avatar_sets'] = AvatarSetSerializer(avatar_sets, many=True).data
        data['gamma_user_info'] = GammaUserInfoSerializer.get_gamma_user_info(user_uid)

        return data
