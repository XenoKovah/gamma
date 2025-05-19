import pytest
from schematics.types import IntType, StringType

from events.schemas import CountActionSchema, RggPointDistributionSchema
from events.utils import SchemaRenderer

pytestmark = pytest.mark.django_db


class TestSchemaRenderer:
    """
    Test SchemaRenderer util.
    """

    @pytest.mark.parametrize('event_type_name, expected_schema_class', [
        ('rgg_points_distribution', RggPointDistributionSchema),
        ('problem_graded', CountActionSchema),
        ('unknown_event', CountActionSchema),
    ])
    def test_get_schema_for_event_type(self, event_type_name, expected_schema_class):
        renderer = SchemaRenderer()

        assert renderer.get_schema_for_event_type(event_type_name) == expected_schema_class

    @pytest.mark.parametrize('field, expected_type', [
        (IntType(), 'integer'),
        (StringType(), 'string'),
    ])
    def test_get_field_type_known(self, field, expected_type):
        assert SchemaRenderer.get_field_type(field) == expected_type

    def test_get_field_type_unknown(self):
        class DummyField:
            pass

        assert SchemaRenderer.get_field_type(DummyField()) == 'Unknown'

    @pytest.mark.parametrize('event_type_name, expected_fields', [
        (
            'rgg_points_distribution',
            [{'field': 'points', 'title': 'Number of points required', 'type': 'integer', 'required': True}]
        ),
        (
            'problem_graded',
            [{'field': 'count', 'title': 'Number of repetitions required', 'type': 'integer', 'required': True}]
        ),
        (
            'unknown_event',
            [{'field': 'count', 'title': 'Number of repetitions required', 'type': 'integer', 'required': True}]
        ),
    ])
    def test_render_schema(self, event_type_name, expected_fields):
        renderer = SchemaRenderer()
        schema = renderer.render_schema(event_type_name)

        assert schema == expected_fields
