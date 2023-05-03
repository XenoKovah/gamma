import os

import pymongo


EVENT_HISTORY_DB_INDEXES = [("uid", pymongo.ASCENDING),
                            ("user_uid", pymongo.ASCENDING),
                            ("client", pymongo.ASCENDING)]

USERS_INDEXES = [("user_uid", pymongo.ASCENDING)]


class Singleton(object):  # pylint: disable=useless-object-inheritance
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class MongoConnector(Singleton):
    """
    Mongo connector as singleton object to utilize mongo connection pool.
    """

    _db = None

    @property
    def db(self):
        if not self._db:
            mongo_database = os.getenv('MONGO_DATABASE')
            assert mongo_database
            self._mongo_init(mongo_database)
        return self._db

    def _mongo_init(self, mongo_database):
        """
        Set class _db variable.
        """
        mongo_url = os.getenv('MONGO_URL')
        assert mongo_url

        client = pymongo.MongoClient(mongo_url)

        self._db = client[mongo_database]

        self._db.users.create_index(USERS_INDEXES, unique=True)
        self._db.event_history.create_index(EVENT_HISTORY_DB_INDEXES, unique=True)

conn = MongoConnector()


def health():
    """
    Health check for MongoDB.

    Do ping and serverStatus commands.
    """
    return conn.db.command('ping'), conn.db.command('serverStatus')
