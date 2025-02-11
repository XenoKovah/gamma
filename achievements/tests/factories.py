import factory
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType

from achievements.models import AchievementRule


class AchievementFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Achievement instances.
    """

    user = factory.SubFactory('users.factories.GammaUserFactory')
    uuid = factory.Faker('uuid4')
    content_type = factory.LazyAttribute(lambda _: ContentType.objects.get_for_model('badges.Badge'))
    object_id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = 'achievements.Achievement'


class AchievementRuleFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating AchievementRule instances.
    """

    status = AchievementRule.Statuses.ACTIVE
    achievement = factory.SubFactory(AchievementFactory)
    rule = factory.SubFactory('rules.factories.RuleFactory')
    created_at = factory.LazyFunction(now)
    dependencies = factory.LazyAttribute(lambda _: {'badge': 'dependency_id'})

    class Meta:
        model = 'achievements.AchievementRule'
