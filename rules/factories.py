import factory

from events.factories import EventConfigurationFactory


class RuleFactory(factory.django.DjangoModelFactory):
    """
    Factory for the Rule model.
    """

    event_configuration = factory.SubFactory(EventConfigurationFactory)
    action = factory.Dict({
        'stop_video': factory.Faker('pyint'),
        'edx_course_enrollment_activated': factory.Faker('pyint'),
    })
    filters = factory.Dict({
        'org': factory.Faker('company'),
        'course': 'course-v1:test+1+1',
        'frequency': factory.Faker('pyint'),
    })

    class Meta:
        model = 'rules.Rule'
