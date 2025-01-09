from rest_framework import serializers
from events.models import Event, EventConfiguration


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = [
            'uid', 
            'signup_source', 
            'username', 
            'event_type', 
            'title', 
            'points', 
            'date', 
            'client', 
            'org', 
            'course_id'
        ]

    def validate_event_type(self, value):
        if not EventConfiguration.objects.filter(event_type=value).exists():
            raise serializers.ValidationError('Event type is not recognizable')
        return value
