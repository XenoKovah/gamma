import logging

import pymongo
from django.conf import settings

from core.services import MongoConnector


logger = logging.getLogger('events')


# TODO maybe need to move all this logic to core.services.MongoConnector

from django.core.files.base import ContentFile
import base64

def base64_to_file(data_attachment, prefix='image'):
    """
    convert base64 attachment string to django File
    :return: django ContentFile
    """
    if data_attachment and data_attachment.startswith('data:image'):
        format, image_string = data_attachment.split(';base64,')
        extension = format.split('/')[-1].split('+')[0]
        name = '{}.{}'.format(prefix, extension)
        return ContentFile(base64.b64decode(image_string), name=name)
    return None

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

    def upsert_rule(self, achievement_slug, rules):
        try:
            self.collection.find_one_and_update(
                filter={'slug': achievement_slug},
                update={'$set': {'rules': rules}},
                upsert=True
            )
        except Exception as e:
            logger.debug('MongoDB Exception: {0}::badge_slug=>{1}::rules=>{2}'.format(
                e, achievement_slug, rules
            ))
