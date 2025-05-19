from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.types import IntType, StringType

from achievements.enums import AchievementTypes


class CountActionSchema(Model):
    """
    The common schema of action using count field.

    The rule using a counter that is responsible for the number of necessary repetitions to execute the rule.
    """

    count = IntType(required=True, metadata={'title': 'Number of repetitions required'})


class RggAchievementObtainedSchema(Model):
    """
    The common schema of action using for dependent object(avatars evolution).
    """

    dependent_object_id = IntType(required=True, metadata={'title': 'Dependent object ID'})
    dependent_content_type = StringType(
        required=True, metadata={'title': 'Dependent Content Type'}, choices=AchievementTypes.get_all()
    )

    def validate_dependent_content_type(self, data, value):
        if value not in AchievementTypes.get_all():
            raise ValidationError('Invalid achievement type: %s', value)
        return value


class RggPointDistributionSchema(Model):
    """
    The common schema of action using for user points distribution.
    """

    points = IntType(required=True, metadata={'title': 'Number of points required'})
