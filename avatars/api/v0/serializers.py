from django.core.files.uploadedfile import SimpleUploadedFile
from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers

from avatars.constants import (
    AVATAR_SET_DUPLICATE_TITLE_ERROR,
    AVATAR_SET_TITLE_ERROR,
    AVATAR_SHOULD_CONTAINS_AT_LEAST_ONE_RULE,
    AVATAR_STAGES_ERROR,
    AVATAR_TITLE_ERROR,
    INVALID_FILE_FORMAT,
    SVG_EXTENSION
)
from avatars.models import Avatar, AvatarSet, UserAvatarConfig
from rules.models import Rule
from rules.serializers import RuleSerializer
from users.models import GammaUser
from users.utils import get_received_user_avatars_ids


class Base64SVGField(Base64FileField):
    """
    Custom class for working with base64 encoded files.

    `ALLOWED_TYPES` and `get_file_extension` are part of the implementation
    of the parent class.
    """

    ALLOWED_TYPES = [SVG_EXTENSION]

    def to_internal_value(self, data):
        """
        Validate received encoded file.
        """
        if isinstance(data, str) and data.startswith('data:image/svg+xml;base64'):
            return super().to_internal_value(data)
        elif isinstance(data, SimpleUploadedFile):
            return data
        raise serializers.ValidationError(INVALID_FILE_FORMAT)

    def get_file_extension(self, filename, decoded_file):
        """
        Return allowed extensions for encoded files.
        """
        return SVG_EXTENSION


class AvatarSerializer(serializers.ModelSerializer):
    """
    Serializer for Avatar model.
    """

    # DRF Serializer Behavior
    # If your serializer is expecting nested objects and is using a ModelSerializer,
    # it might not be recognizing the `id` field when parsing the request data.
    # So, I added `existent_id` optional field.
    existent_id = serializers.IntegerField(required=False)
    image = Base64SVGField()
    rules = RuleSerializer(many=True, required=False)

    class Meta:
        model = Avatar
        fields = ('id', 'title', 'description', 'image', 'rules', 'existent_id', 'stage', 'created_at')
        read_only_fields = ('created_at',)

    def update(self, instance, validated_data):
        """
        Handle updates to a single Avatar, including updating rules.
        """
        rules_data = validated_data.pop('rules', None)

        if not rules_data:
            raise serializers.ValidationError(AVATAR_SHOULD_CONTAINS_AT_LEAST_ONE_RULE)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if rules_data is not None:
            instance.rules.clear()
            for rule_data in rules_data:
                rule, __ = Rule.objects.get_or_create(**rule_data)
                instance.rules.add(rule)

        return instance

    def validate(self, data):
        """
        Ensure Avatar has both title and image.
        """
        if not data.get('title'):
            raise serializers.ValidationError(AVATAR_TITLE_ERROR)
        return data


class AvatarSetSerializer(serializers.ModelSerializer):
    """
    AvatarSet serializer.
    """

    avatars = AvatarSerializer(many=True, required=False)

    class Meta:
        model = AvatarSet
        fields = ('id', 'title', 'avatars', 'use_in_courses', 'is_draft', 'created_at')
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        """
        Handle creation of the AvatarSet on first step, needs only valid tittle for creation.
        """
        avatar_set = AvatarSet.objects.create(**validated_data)
        return avatar_set

    def update(self, instance, validated_data):
        """
        Ensures at least two Avatar objects exist in the AvatarSet before updating.
        """
        avatars_data = validated_data.pop('avatars', None)

        if avatars_data is not None:
            if len(avatars_data) < 2:
                raise serializers.ValidationError(AVATAR_STAGES_ERROR)

            avatar_serializer = AvatarSerializer(data=avatars_data, many=True)
            avatar_serializer.is_valid(raise_exception=True)

            avatar_instances = []
            for av in avatars_data:
                avatar_instance, __ = Avatar.objects.update_or_create(
                    id=av.get('existent_id'),
                    defaults={
                        'title': av.get('title'),
                        'description': av.get('description'),
                        'image': av.get('image'),
                        'stage': av.get('stage'),
                    }
                )
                avatar_instances.append(avatar_instance)
            instance.avatars.set(avatar.id for avatar in avatar_instances)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def validate_title(self, value):
        """
        Validation for the title field, ensures title is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError(AVATAR_SET_TITLE_ERROR)

        if self.instance and self.instance.title == value:
            return value

        if AvatarSet.objects.filter(title=value).exists():
            raise serializers.ValidationError(AVATAR_SET_DUPLICATE_TITLE_ERROR)

        return value


class UserAvatarConfigSerializer(serializers.ModelSerializer):
    """

    """

    gamma_user_id = serializers.PrimaryKeyRelatedField(
        source='user', queryset=GammaUser.objects.all()
    )
    selected_avatar_id = serializers.PrimaryKeyRelatedField(
        source='selected_avatar', queryset=Avatar.objects.all(), allow_null=True, required=False
    )
    selected_avatar_set_id = serializers.PrimaryKeyRelatedField(
        source='avatar_set', queryset=AvatarSet.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = UserAvatarConfig
        fields = ('id', 'gamma_user_id', 'selected_avatar_id', 'selected_avatar_set_id')

        read_only_fields = ('selected_avatar_id',)

    def create(self, validated_data):
        """
        Add `selected_avatar_id` to User Avatar Set config if it exists.
        """
        user_avatar_config = super().create(validated_data)

        gamma_user = validated_data.pop('user', None)
        selected_avatar_set = validated_data.pop('avatar_set', None)

        latest_user_avatar_id = self.get_latest_user_avatar_id_for_set(selected_avatar_set, gamma_user)
        user_avatar_config.selected_avatar_id = latest_user_avatar_id
        user_avatar_config.save()

        return user_avatar_config

    def update(self, instance, validated_data):
        """
        Add `selected_avatar_id` to User Avatar Set config if it exists.
        """
        instance = super().update(instance, validated_data)

        gamma_user = validated_data.pop('user', None)
        selected_avatar_set = validated_data.pop('avatar_set', None)

        latest_user_avatar_id = self.get_latest_user_avatar_id_for_set(selected_avatar_set, gamma_user)
        instance.selected_avatar_id = latest_user_avatar_id
        instance.save()

        return instance

    def get_latest_user_avatar_id_for_set(self, avatar_set=None, gamma_user=None):
        """
        Get latest received user's Avatar id for given AvatarSet.
        """
        if avatar_set and gamma_user:
            ordered_avatar_ids = avatar_set.get_ordered_avatar_ids_from_set()
            received_user_avatars_ids = get_received_user_avatars_ids(gamma_user.user_uid)

            for avatar_id in ordered_avatar_ids:
                if avatar_id in received_user_avatars_ids:
                    return avatar_id

        return None
