from datetime import datetime

from rest_framework import serializers
from schematics.exceptions import DataError

from events.api.v0.serializers import EventConfigurationSerializer
from events.models import EventConfiguration
from events.utils import SchemaRenderer

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


class CourseFilterField(serializers.Field):
    """
    Accept a single course id (string) or a list of course ids.

    A list means "a certificate in any of these courses" (an OR group), used to credit
    students for any accepted version of a course. The list is de-duplicated and sorted so
    equivalent filters dedupe to the same Rule.
    """

    def to_internal_value(self, data):
        if isinstance(data, str):
            return data
        if isinstance(data, (list, tuple)) and all(isinstance(item, str) for item in data):
            return sorted(set(data))
        raise serializers.ValidationError('course must be a string or a list of strings.')

    def to_representation(self, value):
        return value


class CompletionWindowFilterSerializer(serializers.Serializer):
    """
    Validate the completion window: how long the learner took to finish the class.

    Measured in whole weeks from their first activity in the class to the event being
    processed. ``min_weeks`` is exclusive and ``max_weeks`` inclusive, so bands laid
    end to end (0-2, 2-4, 4-12, 12+) tile without overlapping and award one tier.

    ``match_without_anchor`` marks the band that also claims learners whose pace cannot
    be measured at all; it belongs on a single open-ended band of a set.
    """

    min_weeks = serializers.IntegerField(required=False, min_value=0)
    max_weeks = serializers.IntegerField(required=False, min_value=1)
    match_without_anchor = serializers.BooleanField(required=False)

    def validate(self, attrs):
        lower, upper = attrs.get('min_weeks'), attrs.get('max_weeks')

        # A window carrying only match_without_anchor would match every pace as well as
        # the unmeasurable case, silently swallowing the graded bands.
        if lower is None and upper is None:
            raise serializers.ValidationError('completion_window requires min_weeks and/or max_weeks.')

        if upper is not None and lower is not None and upper <= lower:
            raise serializers.ValidationError('max_weeks must be greater than min_weeks.')

        return attrs


class FiltersSerializer(serializers.Serializer):
    """
    Serializer for validating the filters in a rule.
    """

    interval = IntervalFilterSerializer(required=False)
    org = serializers.CharField(required=False)
    frequency = serializers.IntegerField(required=False)
    course = CourseFilterField(required=False)
    completion_window = CompletionWindowFilterSerializer(required=False)


class RuleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rule model.
    """

    action = serializers.JSONField()
    filters = FiltersSerializer(required=False, allow_null=True)
    event_configuration = EventConfigurationSerializer()

    class Meta:
        model = Rule
        fields = ('id', 'event_configuration', 'action', 'filters', 'created_at')
        read_only_fields = ('created_at',)

    def validate_action(self, value):
        """
        Validate and process the action field.

        Expected `action_value` for different Event Types:
            - `rgg_points_distribution`: {'points': 30}
            - `rgg_achievement_obtained`: {'dependent_object_id': 1, 'dependent_content_type': 'string'}
            - default edX events: {'count': 5}
        """
        if not isinstance(value, dict) or len(value) != 1:
            raise serializers.ValidationError('Action must contain exactly one event type.')

        valid_event_names = EventConfiguration.all_event_names()
        event_name, action_value = next(iter(value.items()))

        if event_name not in valid_event_names:
            raise serializers.ValidationError(
                f'Invalid event type {event_name!r} in action. Must match an existing EventConfiguration.'
            )

        try:
            current_schema = SchemaRenderer().get_schema_for_event_type(event_name)(action_value)
            current_schema.validate()
        except DataError as exc:
            raise serializers.ValidationError(f'Invalid action value {exc} for given Event Type: {event_name}')

        return {event_name: action_value}

    def validate_filters(self, value):
        """
        Validate and process filters field.
        """
        filters_serializer = FiltersSerializer(data=value)
        filters_serializer.is_valid(raise_exception=True)
        return filters_serializer.validated_data
