import re
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


class BlocksFilterField(serializers.Field):
    """
    Accept a single block usage key (string) or a list of usage keys.

    The list is the set of blocks the rule is about — e.g. every "Mark as complete"
    block that makes up a badge — matched against each event's block_id. With the
    action count equal to the list length the rule reads "all of these blocks". The
    list is de-duplicated and sorted so equivalent filters dedupe to the same Rule.
    """

    def to_internal_value(self, data):
        if isinstance(data, str):
            data = [data]
        if (
            isinstance(data, (list, tuple))
            and data
            and all(isinstance(item, str) and item.strip() for item in data)
        ):
            return sorted({item.strip() for item in data})
        raise serializers.ValidationError('blocks must be a usage key or a non-empty list of usage keys.')

    def to_representation(self, value):
        return value


class FiltersSerializer(serializers.Serializer):
    """
    Serializer for validating the filters in a rule.
    """

    interval = IntervalFilterSerializer(required=False)
    org = serializers.CharField(required=False)
    frequency = serializers.IntegerField(required=False)
    course = CourseFilterField(required=False)
    blocks = BlocksFilterField(required=False)

    COURSE_FROM_BLOCK_KEY = re.compile(r'^block-v1:(?P<course>[^+]+\+[^+]+\+[^+]+)\+type@')

    def validate(self, attrs):
        """
        Derive the course filter from the blocks filter when absent.

        Course-scoped features (per-course badge lists, the course leaderboard's badge
        column) associate a badge with a course through its rules' course filter, so a
        block-set rule should carry the course(s) its blocks live in even when the
        admin only entered block keys.
        """
        if attrs.get('blocks') and not attrs.get('course'):
            courses = sorted({
                f'course-v1:{match.group("course")}'
                for block in attrs['blocks']
                if (match := self.COURSE_FROM_BLOCK_KEY.match(block))
            })
            if courses:
                attrs['course'] = courses if len(courses) > 1 else courses[0]
        return attrs


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
