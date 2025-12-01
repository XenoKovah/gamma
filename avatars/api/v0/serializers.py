from typing import Optional

from django.core.files.uploadedfile import SimpleUploadedFile
from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers

from achievements.services.progress import AvatarProgressService
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
                rule_data['filters'] = {}
                rule = Rule.ensure_rule_is_created_from_data(rule_data)
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
        fields = ('id', 'title', 'avatars', 'is_draft', 'created_at')
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
    Serializer for UserAvatarConfig.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=GammaUser.objects.all())
    avatar_set = serializers.PrimaryKeyRelatedField(queryset=AvatarSet.objects.all(), allow_null=True, required=False)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserAvatarConfig
        fields = ('id', 'user', 'avatar_set', 'avatar')
        read_only_fields = ('id', 'avatar')

    def get_avatar(self, instance) -> Optional[Avatar]:
        """
        Get last achieved avatar.
        """
        progress = AvatarProgressService(instance)
        last = progress.resolve_current()
        return AvatarSerializer(last, context=self.context).data if last else None


class AvatarProgressSerializer(serializers.Serializer):
    """
    Serializer for user avatar progress.
    """

    current_points = serializers.IntegerField()
    required_points = serializers.IntegerField()
    current_avatar = serializers.DictField(allow_null=True)
    next_avatar = serializers.DictField(allow_null=True)
