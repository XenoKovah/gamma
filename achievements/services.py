from abc import ABCMeta


class AchivementRulesABS(metaclass=ABCMeta):
    pass


class AchivementRulesMongo:
    """
    Class to work with Mongo.
    """
    def __init__(self, collection, type):
        """
        `collection`: Mongo collection
        `type`: event type
        """
        document = collection.find_one({"type": type})
        return document
