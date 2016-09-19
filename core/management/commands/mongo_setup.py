from datetime import datetime

from pymongo import MongoClient
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from core.utils import MongoConnector


class Command(BaseCommand):
    help = 'Populate MongoDB with default settings.'

    def handle(self, *args, **options):
        conn = MongoConnector()
        settings_collection = conn.db[settings.MONGO_SETTINGS_COLLECTION]
        settings_collection.remove()
        settings_collection.insert_one({
            "video": 6,
            "problem": 7,
            "course": 11,
            "enrollment": 5,
            "referrer": 10
        })
        self.stdout.write(self.style.SUCCESS('Mongo was successfully populated'))
