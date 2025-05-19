from rest_framework import serializers

from events.models import Event, EventConfiguration, EventType
from events.utils import SchemaRenderer


class AvailableActionsSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField()
    schema = serializers.SerializerMethodField()

    class Meta:
        model = EventConfiguration
        fields = ('id', 'event_name', 'title', 'schema')

    def get_schema(self, obj):
        """
        Get current schema for given Event Type.
        """
        return SchemaRenderer().render_schema(event_type_name=obj.event_type.name)


class EventConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventConfiguration model.
    """

    event_type = serializers.CharField(source='event_type.name')

    class Meta:
        model = EventConfiguration
        fields = ('event_type', 'title', 'award')

    def to_internal_value(self, data):
        """
        Allow passing either an ID or a full object.

        Resolve to an EventConfiguration instance or create new one.
        """
        if isinstance(data, int):
            try:
                return EventConfiguration.objects.get(id=data)
            except EventConfiguration.DoesNotExist:
                raise serializers.ValidationError('EventConfiguration with this ID does not exist.')

        elif isinstance(data, dict):
            event_type_name = data.get('event_type')
            if not event_type_name:
                raise serializers.ValidationError({'event_type': 'This field is required.'})

            try:
                event_type_obj = EventType.objects.get(name=event_type_name)
            except EventType.DoesNotExist:
                raise serializers.ValidationError({'event_type': f'No such event_type: {event_type_name}'})

            data.update({'event_type': event_type_obj.id})
            instance, _ = EventConfiguration.objects.get_or_create(**data)
            return instance

        elif isinstance(data, EventConfiguration):
            return data
        else:
            raise serializers.ValidationError('Invalid event_configuration input.')


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for Event model.
    """

    event_type = serializers.CharField(write_only=True)
    configuration = EventConfigurationSerializer(read_only=True)

    class Meta:
        model = Event
        fields = (
            'uid',
            'signup_source',
            'username',
            'created_at',
            'client',
            'org',
            'course_id',
            'configuration',
            'event_type',
        )

    def validate_event_type(self, value):
        """
        Validate that the provided event_type exists.
        """
        if not (configuration := EventConfiguration.objects.filter(event_type__name=value).last()):
            raise serializers.ValidationError('Error: Event type is not recognizable')

        self.context['configuration'] = configuration
        return value

    def create(self, validated_data):
        """
        Override for the create method to set the `configuration` as ForeignKey for Event instance.
        """
        configuration = self.context['configuration']
        validated_data['configuration'] = configuration
        validated_data.pop('event_type')
        return super().create(validated_data)
