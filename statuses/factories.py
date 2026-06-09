import factory
from django.utils.text import slugify


class StatusFactory(factory.django.DjangoModelFactory):
    """
    Factory for the Status model.
    """

    class Meta:
        model = 'statuses.Status'

    title = factory.Faker('sentence', nb_words=2)
    status_points = factory.Sequence(lambda n: (n + 1) * 100)
    color = ''
    image = factory.django.ImageField(color='blue')
    is_active = True
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
