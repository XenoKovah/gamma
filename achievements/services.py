import pymongo
from django.conf import settings

from core.utils import MongoConnector


# TODO maybe need to move all this logic to core.utils.MongoConnector
class AchievementRulesMongo:
    """
    Class to work with Mongo.
    """
    def connect(self):
        conn = MongoConnector()
        self.collection = conn.db[
            settings.MONGO_RULES_COLLECTION
        ]

    def get_rule(self, achievement_slug):
        """
        Return rules for particular achievement.
        """
        try:
            rules = self.collection.find_one(
                {'slug': achievement_slug}
            ).get('rules')
        except Exception:
            rules = None
        return rules

    def upsert_rule(self, achievement_slug, rules):
        try:
            self.collection.find_one_and_update(
                filter={'slug': achievement_slug},
                update={'$set': {'rules': rules}},
                upsert=True
            )
        except Exception as e:
            # TODO configure Django Logging for this case
            print(e)
