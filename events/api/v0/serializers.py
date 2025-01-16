from rest_framework import serializers

from events.models import Event, EventConfiguration


class EventConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventConfiguration model.
    """

    event_type = serializers.CharField(source='event_type.name')

    class Meta:
        model = EventConfiguration
        fields = ('event_type', 'title', 'award', 'color', 'notification_message')


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
