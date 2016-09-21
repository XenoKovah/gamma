import hashlib
from uuid import uuid4

import pymongo
from django.conf import settings


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class MongoConnector(Singleton):
    """
    Mongo connector as singleton object to utilize
    mongo connection pool.
    """
    _db = None

    @property
    def db(self):
        if not self._db:
            self._mongo_init()
        return self._db

    def _mongo_init(self):
        """
        Set class _db variable.
        """
        client = pymongo.MongoClient(
            settings.MONGODB_CONF.get('HOST', 'localhost'),
            settings.MONGODB_CONF.get('PORT', 27017),
        )
        self._db = client[settings.MONGO_DB_NAME]

        username = settings.MONGODB_CONF.get('USERNAME')
        password = settings.MONGODB_CONF.get('PASSWORD')

        if username and password:
            self._db.authenticate(username, password, source=settings.MONGO_DB_NAME)

    def find_one_and_update(self, filter_dict, key, value, event_type=None):
        """
        Find and update Mongo document.

        Find document in mongo collection by `filter_by` search param
        and update(increment) particular field by `key`.
        """
        if event_type:
            collection = self.db[
                settings.MONGO_CHARTED_PROGRESS
            ]
        else:
            collection = self.db[
                settings.MONGO_PROGRESS_COLLECTION
            ]
        try:
            document = collection.find_one_and_update(
                filter=filter_dict,
                update={'$inc': {key: value}},
                upsert=True,
                return_document=pymongo.ReturnDocument.AFTER
            )
        except Exception as e:
            # TODO configure Django Logging for this case
            print(e)

    def get_progress(self, user):
        """
        Get progress data from MongoDB.
        """
        collection = self.db[
            settings.MONGO_PROGRESS_COLLECTION
        ]
        progress_data = collection.find(
            {"username": user.username}, {"date": 1, "points": 1, "_id": 0}
        ).sort("date", pymongo.DESCENDING).limit(7)
        return progress_data

    def get_charted_progress(self, user):
        collection = self.db[
            settings.MONGO_CHARTED_PROGRESS
        ]
        charted_progress = collection.find_one(
            {"username": user.username},
            {"video": 1, "course": 1, "problem": 1, "enrollment": 1, "referrer": 1, "_id": 0}
        )
        return charted_progress


def key_secret_generator():
    """
    Generate a key/secret for AppClient.
    """
    hash = hashlib.sha1(uuid4().hex.encode('utf-8'))
    hash.update(settings.SECRET_KEY.encode('utf-8'))
    return hash.hexdigest()[::2]
