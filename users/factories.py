import factory
from factory.django import DjangoModelFactory

from users.models import GammaUser


class GammaUserFactory(DjangoModelFactory):
    """
    Factory for creating Gamma User instances.
    """

    class Meta:
        model = GammaUser

    username = factory.Sequence(lambda n: f'test_gamma_user_{n}')
    user_uid = factory.Faker('uuid4')
    points = 100
    chart = factory.Dict({})
    progress = factory.Dict({})
