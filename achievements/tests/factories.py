import factory
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from pytest_factoryboy import register

from achievements.models import AchievementRule


@register
class AchievementFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Achievement instances.
    """

    user = factory.SubFactory("users.tests.factories.GammaUserFactory")
    uuid = factory.Faker("uuid4")
    content_type = factory.LazyAttribute(lambda _: ContentType.objects.get_for_model("badges.Badge"))
    object_id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")

    class Meta:
        model = "achievements.Achievement"


@register
class AchievementRuleFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating AchievementRule instances.
    """

    status = AchievementRule.Statuses.ACTIVE
    achievement = factory.SubFactory(AchievementFactory)
    rule = factory.SubFactory("rules.tests.factories.RuleFactory")
    created_at = factory.LazyFunction(now)
    dependencies = factory.LazyAttribute(lambda _: {"badge": "dependency_id"})

    class Meta:
        model = "achievements.AchievementRule"
