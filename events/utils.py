import hashlib
import uuid

from schematics.types import IntType, StringType

from events.schemas import CountActionSchema, RggPointDistributionSchema


def simulate_rgg_internal_event(user: 'GammaUser', event_name: str):
    """
    Simulate an internal RGG event for a given user.
    """
    from events.models import Event, EventConfiguration

    configuration = EventConfiguration.objects.filter(event_type__name=event_name).first()
    if not configuration:
        raise ValueError(
            f'There is no any event configuration found for {event_name!r}. '
            'Please setup it.'
        )

    Event.ensure_internal_event_is_created(user, configuration)


class SchemaRenderer:
    """
    Render schema according to the given Event Type.
    """

    EVENT_SCHEMA_MAP = {
        'rgg_points_distribution': RggPointDistributionSchema,
        'rgg_continuous_learning_streak': CountActionSchema,
        'rgg_continuous_learning_weekday_streak': CountActionSchema,
    }

    FIELD_TYPE_MAP = {
        IntType: 'integer',
        StringType: 'string',
    }

    def render_schema(self, event_type_name):
        schema_class = self.get_schema_for_event_type(event_type_name)

        fields = schema_class.fields
        result = []

        for name, field in fields.items():
            result.append({
                'field': name,
                'title': field.metadata.get('title'),
                'type': self.get_field_type(field),
                'required': field.required
            })

        return result

    def get_schema_for_event_type(self, event_type_name):
        return self.EVENT_SCHEMA_MAP.get(event_type_name, CountActionSchema)

    @classmethod
    def get_field_type(cls, field):
        return cls.FIELD_TYPE_MAP.get(type(field), 'Unknown')


def uid_generator():
    """
    Generate a uid for internal Event.
    """
    input_data = str(uuid.uuid4())
    hash_hex = hashlib.sha1(input_data.encode()).hexdigest()
    return hash_hex
