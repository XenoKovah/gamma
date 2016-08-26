import pymongo
from django.conf import settings


CLIENT = pymongo.MongoClient()


def find_one_and_update(filter_dict, key, value):
    """
    Find and update Mongo document.

    Find document in mongo collection by `filter_by` search param
    and update(increment) particular field by `key`.
    """
    db = CLIENT[settings.MONGO_DB_NAME]
    collection = db[settings.MONGO_PROGRESS_COLLECTION]

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
