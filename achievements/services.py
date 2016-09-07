import pymongo
from django.conf import settings


class AchievementRulesMongo:
    """
    Class to work with Mongo.
    """
    def __init__(self):
        client = pymongo.MongoClient(
            settings.MONGODB_CONF.get('HOST', 'localhost'),
            settings.MONGODB_CONF.get('PORT', 27017),
        )
        db = client[settings.MONGO_DB_NAME]

        username = settings.MONGODB_CONF.get('USERNAME')
        password = settings.MONGODB_CONF.get('PASSWORD')

        if username and password:
            db.authenticate(username, password, source=settings.MONGO_DB_NAME)

        self.collection = db[settings.MONGO_RULES_COLLECTION]

    def get_rule(self, achievement_slug):
        """
        Return rules for particular achievement.
        """
        return self.collection.find_one(
            {'slug': achievement_slug}
        ).get('rules')

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
