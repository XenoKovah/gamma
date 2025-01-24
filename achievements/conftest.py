from pytest_factoryboy import register

from .factories import AchievementFactory, AchievementRuleFactory

register(AchievementFactory)
register(AchievementRuleFactory)
