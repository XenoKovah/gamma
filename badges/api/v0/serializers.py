import base64
import imghdr

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
                return ContentFile(decoded_file, name=f'temp.{imghdr.what(None, decoded_file)}')
            except Exception:
                raise serializers.ValidationError('Invalid image format')
        return super().to_internal_value(data)


class BadgeSerializer(serializers.ModelSerializer):
    rules = RuleSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Badge
        fields = ('id', 'title', 'description', 'image', 'is_active', 'slug', 'rules')

    def create(self, validated_data):
        """
        Handle creation of a badge, including creating or linking rules.
        """
        rules_data = validated_data.pop('rules', [])
        badge = Badge.objects.create(**validated_data)

        for rule_data in rules_data:
            rule, _ = Rule.objects.get_or_create(**rule_data)
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
                rule, _ = Rule.objects.get_or_create(**rule_data)
                instance.rules.add(rule)

        return instance
