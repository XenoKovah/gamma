import factory
from django.utils.text import slugify
from pytest_factoryboy import register


@register
class BadgeFactory(factory.django.DjangoModelFactory):
    """
    Factory for the Badge model.
    """

    class Meta:
        model = "badges.Badge"

    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph", nb_sentences=2)
    image = factory.django.ImageField(color="blue")
    is_active = True
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    @factory.post_generation
    def set_rules(self, create, extracted, **kwargs):
        """
        Add related Rule objects after Badge creation.
        """
        if not create or not extracted:
            return

        if extracted:
            if isinstance(extracted, tuple) and len(extracted):
                self.rules.set(extracted)
            else:
                self.rules.add(extracted)
