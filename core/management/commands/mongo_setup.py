from pymongo import MongoClient
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Populate MongoDB with default settings.'

    def handle(self, *args, **options):
        client = MongoClient()
        db = client[settings.MONGO_DB_NAME]
        collection = db[settings.MONGO_SETTINGS_COLLECTION]
        collection.remove()
        collection.insert_one({"video": 6, "unit": 7, "course": 11})

        self.stdout.write(self.style.SUCCESS('Mongo was successfully populated'))
