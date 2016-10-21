import logging

import pymongo
from django.conf import settings

from .models import Event


logger = logging.getLogger('events')


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
            logger.debug(
                'MongoDB Exception: {0}::filter_dict=>{1}::key=>{2}::value=>{3}'.format(
                    e, filter_dict, key, value
                )
            )

    def get_progress(self, user):
        """
        Get progress data from MongoDB.

        # TODO change this to request username as string
        user: Django User isinstance
        """
        collection = self.db[
            settings.MONGO_PROGRESS_COLLECTION
        ]
        try:
            progress_data = collection.find(
                {"username": user.username}, {"date": 1, "points": 1, "_id": 0}
            ).sort("date", pymongo.DESCENDING).limit(7)
            return progress_data
        except Exception as e:
            logger.debug('MongoDB Exception: {0}::user=>{1}'.format(
                e, user.username
            ))

    def get_charted_progress(self, user):
        projection = {event.event_type: 1 for event in Event.objects.all()}
        projection['_id'] = 0
        collection = self.db[
            settings.MONGO_CHARTED_PROGRESS
        ]
        try:
            charted_progress = collection.find_one(
                {"username": user.username},
                projection
            )
            return charted_progress
        except Exception as e:
            logger.debug('MongoDB Exception: {0}::user=>{1}'.format(
                e, user.username
            ))
