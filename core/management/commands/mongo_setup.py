from datetime import datetime

from pymongo import MongoClient
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Populate MongoDB with default settings.'

    def handle(self, *args, **options):
        client = MongoClient(
            settings.MONGODB_CONF.get('HOST', 'localhost'),
            settings.MONGODB_CONF.get('PORT', 27017),
        )
        db = client[settings.MONGO_DB_NAME]

        settings_collection = db[settings.MONGO_SETTINGS_COLLECTION]
        settings_collection.remove()
        settings_collection.insert_one({"video": 6, "unit": 7, "course": 11})

        rules_collection = db[settings.MONGO_RULES_COLLECTION]
        default_rules = {
            "date": datetime.now(),
            "type": None,
            "badges": [
                {
                    "badge_slug": "default_slug",
                    "rule": {"count": 10, "type": "default_type"}
                }
            ]
        }
        for event_type in ('video', 'unit', 'course'):
            default_rules['type'] = event_type
            rules_collection.insert_one(default_rules)
            del(default_rules['_id'])

        self.stdout.write(self.style.SUCCESS('Mongo was successfully populated'))
