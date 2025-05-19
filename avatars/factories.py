import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from avatars.models import Avatar, AvatarSet, UserAvatarConfig


class AvatarFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Avatar instances.
    """

    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=100)
    image = factory.LazyAttribute(
        lambda _: SimpleUploadedFile('test_avatar.svg', b'<svg></svg>', content_type='image/svg+xml')
    )

    @factory.post_generation
    def set_rules(self, create, extracted, **kwargs):
        """
        Add related Rule objects after avatar creation.
        """
        if not create or not extracted:
            return

        if extracted:
            if isinstance(extracted, tuple) and len(extracted):
                self.rules.set(extracted)
            else:
                self.rules.add(extracted)

    class Meta:
        model = Avatar


class AvatarSetFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating AvatarSet instances.
    """

    title = factory.Faker('sentence', nb_words=4)
    is_draft = factory.Faker('boolean')

    @factory.post_generation
    def avatars(self, create, extracted, **kwargs):
        """
        If avatars are provided, add them to the set. Otherwise, create two default avatars.
        """
        if not create:
            return

        if extracted:
            self.avatars.set(extracted)
        else:
            self.avatars.set(AvatarFactory.create_batch(2))

    class Meta:
        model = AvatarSet


class UserAvatarConfigFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating UserAvatarConfig instances.
    """

    user = factory.SubFactory('users.factories.GammaUserFactory')
    avatar_set = factory.SubFactory('avatars.factories.AvatarSetFactory')

    class Meta:
        model = UserAvatarConfig
