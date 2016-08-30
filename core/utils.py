import hashlib
from uuid import uuid4

import pymongo
from django.conf import settings


CLIENT = pymongo.MongoClient()
DB = CLIENT[settings.MONGO_DB_NAME]


def find_one_and_update(filter_dict, key, value):
    """
    Find and update Mongo document.

    Find document in mongo collection by `filter_by` search param
    and update(increment) particular field by `key`.
    """

    collection = DB[settings.MONGO_PROGRESS_COLLECTION]
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


def get_progress(user):
    """
    Get progress data from MongoDB.
    """
    collection = DB[settings.MONGO_PROGRESS_COLLECTION]
    progress_data = collection.find(
        {"username": user.username}, {"date": 1, "points": 1, "_id": 0}
    ).sort("date", pymongo.DESCENDING).limit(7)
    return progress_data


def key_secret_generator():
    """
    Generate a key/secret for AppClient.
    """
    hash = hashlib.sha1(uuid4().hex.encode('utf-8'))
    hash.update(settings.SECRET_KEY.encode('utf-8'))
    return hash.hexdigest()[::2]
