import logging

from django.conf import settings

from core.services import MongoConnector


logger = logging.getLogger('events')


# TODO maybe need to move all this logic to core.services.MongoConnector


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
        except Exception as e:
            logger.debug(
                'MongoDB Exception: {0}::badge_slug=>{1}'.format(e, achievement_slug)
            )
            rules = None
        return rules

    #TODO: REFACTORING IS NEEDED! Should be obtained from MongoDB model eventually.
    def upsert_rule(self, achievement_slug, achievement_title, rules):
        try:
            self.collection.find_one_and_update(
                filter={'slug': achievement_slug},
                update={'$set': {'rules': rules, 'title': achievement_title}},
                upsert=True
            )
        except Exception as e:
            logger.debug('MongoDB Exception: {0}::badge_slug=>{1}::rules=>{2}'.format(
                e, achievement_slug, rules
            ))
