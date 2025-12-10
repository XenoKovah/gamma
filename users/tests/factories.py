import factory
import faker
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from pytest_factoryboy import register

from users.models import GammaUser, GammaUserCoursePoints

fake = faker.Faker()


@register
class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Django User instances.
    """

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "password")
    is_active = True
    is_staff = False
    is_superuser = False


@register
class GammaUserFactory(DjangoModelFactory):
    """
    Factory for creating Gamma User instances.
    """

    class Meta:
        model = GammaUser

    username = factory.Sequence(lambda n: f"test_gamma_user_{n}")
    user_uid = factory.Faker("uuid4")
    points = 100
    chart = factory.Dict({})
    progress = factory.Dict({})


@register
class GammaUserCoursePointsFactory(DjangoModelFactory):
    """
    Factory for creating GammaUserCoursePoints instances.
    """

    gamma_user = factory.SubFactory(GammaUserFactory)
    course_id = factory.LazyFunction(lambda: f"course-v1:{fake.company()}+1+1")
    points = factory.Faker("random_int", min=1, max=100)

    class Meta:
        model = GammaUserCoursePoints
