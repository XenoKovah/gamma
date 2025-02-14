from datetime import datetime

from rest_framework import serializers

from events.models import EventConfiguration

from .constants import DATETIME_FORMAT
from .models import Rule


class DateTimeFieldSerializer(serializers.CharField):
    """
    Custom serializer for datetime fields to ensure they match the required format.
    """

    def to_internal_value(self, data):
        try:
            datetime.strptime(data, DATETIME_FORMAT)
            return data
        except ValueError:
            raise serializers.ValidationError(f'Datetime must match the format {DATETIME_FORMAT!r}.')


class IntervalFilterSerializer(serializers.Serializer):
    """
    Validate the interval filter to ensure that if one of the fields is provided.
    """

    start = DateTimeFieldSerializer(required=False)
    end = DateTimeFieldSerializer(required=False)


class FiltersSerializer(serializers.Serializer):
    """
    Serializer for validating the filters in a rule.
    """

    interval = IntervalFilterSerializer(required=False)
    org = serializers.CharField(required=False)
    frequency = serializers.IntegerField(required=False)
    course = serializers.CharField(required=False)


class RuleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rule model.
    """

    action = serializers.JSONField()
    filters = FiltersSerializer(required=False, allow_null=True)

    class Meta:
        model = Rule
        fields = ('id', 'action', 'filters')

    def validate_action(self, value):
        """
        Validate and process the action field.
        """
        if not isinstance(value, dict) or len(value) != 1:
            raise serializers.ValidationError('Action must contain exactly one event type.')

        valid_event_names = EventConfiguration.all_event_names()
        event_name, action_value = next(iter(value.items()))

        if event_name not in valid_event_names:
            raise serializers.ValidationError(
                f'Invalid event type {event_name!r} in action. Must match an existing EventConfiguration.'
            )

        return {event_name: action_value}

    def validate_filters(self, value):
        """
        Validate and process filters field.
        """
        filters_serializer = FiltersSerializer(data=value)
        filters_serializer.is_valid(raise_exception=True)
        return filters_serializer.validated_data
