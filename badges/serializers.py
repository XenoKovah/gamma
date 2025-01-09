from rest_framework import serializers

from badges.models import Badge
from rules.models import Rule
from rules.serializers import RuleSerializer


class BadgeSerializer(serializers.ModelSerializer):
    rules = RuleSerializer(many=True)

    class Meta:
        model = Badge
        fields = ['id', 'title', 'description', 'image', 'active', 'slug', 'rules']

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
