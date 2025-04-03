import faker
import factory
from factory.django import DjangoModelFactory

from users.models import GammaUser, GammaUserCoursePoints

fake = faker.Faker()


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


class GammaUserCoursePointsFactory(DjangoModelFactory):
    """
    Factory for creating GammaUserCoursePoints instances.
    """

    gamma_user = factory.SubFactory(GammaUserFactory)
    course_id = factory.LazyFunction(lambda: f'course-v1:{fake.company()}+1+1')
    points = factory.Faker('random_int', min=1, max=100)

    class Meta:
        model = GammaUserCoursePoints
