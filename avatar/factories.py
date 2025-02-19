import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from avatar.models import Avatar, AvatarSet


class AvatarFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Avatar instances.
    """

    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=100)
    image = factory.LazyAttribute(
        lambda _: SimpleUploadedFile('test_avatar.svg', b'<svg></svg>', content_type='image/svg+xml')
    )

    class Meta:
        model = Avatar


class AvatarSetFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating AvatarSet instances.
    """

    title = factory.Faker('sentence', nb_words=4)
    is_draft = factory.Faker('boolean')
    use_in_courses = factory.LazyFunction(lambda: ['course_1', 'course_2'])

    @factory.post_generation
    def avatar(self, create, extracted, **kwargs):
        """
        If avatars are provided, add them to the set. Otherwise, create two default avatars.
        """
        if not create:
            return

        if extracted:
            self.avatar.set(extracted)
        else:
            self.avatar.set(AvatarFactory.create_batch(2))

    class Meta:
        model = AvatarSet
