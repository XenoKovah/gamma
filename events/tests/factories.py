import factory
from django.utils.timezone import now
from pytest_factoryboy import register


@register
class EventTypeFactory(factory.django.DjangoModelFactory):
    """
    Factory for EventType model.
    """

    class Meta:
        model = 'events.EventType'

    name = factory.Faker('word')


@register
class EventConfigurationFactory(factory.django.DjangoModelFactory):
    """
    Factory for EventConfiguration model.
    """

    class Meta:
        model = 'events.EventConfiguration'

    event_type = factory.SubFactory(EventTypeFactory)
    title = factory.Faker('sentence', nb_words=4)
    award = factory.Faker('random_int', min=1, max=100)


@register
class EventFactory(factory.django.DjangoModelFactory):
    """
    Factory for Event model.
    """

    class Meta:
        model = 'events.Event'

    uid = factory.Faker('uuid4')
    signup_source = factory.Faker('word')
    username = factory.Faker('user_name')
    configuration = factory.SubFactory(EventConfigurationFactory)
    created_at = factory.LazyFunction(now)
    client = factory.Faker('user_name')
    org = factory.Faker('company')
    course_id = factory.LazyAttribute(lambda c: f'course-v1:{c.org}+1+1')


@register
class EventRequestDataFactory(factory.Factory):
    class Meta:
        model = dict

    event_type = factory.LazyAttribute(lambda obj: obj.allowed_event_configurations[0].event_type.name)
    username = factory.Faker('user_name')
    signup_source = factory.Faker('word')
    course_id = factory.LazyAttribute(lambda c: f'course-v1:{c.org}+1+1')
    org = factory.Faker('company')
    uid = factory.Faker('uuid4')
    client = factory.Faker('user_name')
