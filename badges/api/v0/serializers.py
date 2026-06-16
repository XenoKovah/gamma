import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers

from badges.models import Badge
from rules.models import Rule
from rules.serializers import RuleSerializer


class Base64ImageField(serializers.ImageField):
    """
    A custom field for handling image uploads through raw base64 encoded data.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                _, imgstr = data.split(';base64,')
                decoded_file = base64.b64decode(imgstr)
                file_extension = imghdr.what(None, decoded_file)
                unique_filename = f"{uuid.uuid4().hex}.{file_extension if file_extension else 'unknown'}"
                return ContentFile(decoded_file, name=unique_filename)
            except Exception:
                raise serializers.ValidationError('Invalid image format')
        return super().to_internal_value(data)


class BadgeSerializer(serializers.ModelSerializer):
    rules = RuleSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Badge
        fields = (
            'id', 'title', 'description', 'category', 'image', 'is_active', 'slug', 'points',
            'manual_criteria', 'rules', 'created_at',
        )
        read_only_fields = ('created_at',)

    def validate(self, attrs):
        """
        Enforce that negative points are only ever set on a manually-assigned
        (rule-less) badge. Checks the combined post-edit state (incoming ``points``
        and ``rules`` fall back to the existing instance when not being changed), so
        a penalty cannot be applied to a badge that has — or is gaining — completion
        rules, and a rule cannot be added to a negative-points badge.
        """
        attrs = super().validate(attrs)

        points = attrs.get('points', getattr(self.instance, 'points', 0) or 0)
        if 'rules' in attrs:
            rules = attrs['rules']
        elif self.instance is not None:
            rules = self.instance.rules.all()
        else:
            rules = []

        if points is not None and points < 0 and rules:
            raise serializers.ValidationError({
                'points': 'Negative points are only allowed on manually-assigned badges with no completion rules.',
            })
        return attrs

    def create(self, validated_data):
        """
        Handle creation of a badge, including creating or linking rules.
        """
        rules_data = validated_data.pop('rules', [])
        badge = Badge.objects.create(**validated_data)

        for rule_data in rules_data:
            rule = Rule.ensure_rule_is_created_from_data(rule_data)
            badge.rules.add(rule)

        return badge

    def update(self, instance, validated_data):
        """
        Handle updates to a badge, including updating rules.
        """
        rules_data = validated_data.pop('rules', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if rules_data is not None:
            instance.rules.clear()
            for rule_data in rules_data:
                rule = Rule.ensure_rule_is_created_from_data(rule_data)
                instance.rules.add(rule)

        return instance


class BadgeAssignmentSerializer(serializers.Serializer):
    """
    Validate the payload for manually assigning a badge to users by their user id.
    """

    user_uids = serializers.ListField(
        child=serializers.CharField(max_length=255, allow_blank=False, trim_whitespace=True),
        allow_empty=False,
        help_text='List of GammaUser user_uids (edX usernames) to grant the badge to.',
    )

    def validate_user_uids(self, value):
        """
        De-duplicate the user ids while preserving order.
        """
        seen = set()
        deduplicated = []
        for user_uid in value:
            if user_uid not in seen:
                seen.add(user_uid)
                deduplicated.append(user_uid)
        return deduplicated
