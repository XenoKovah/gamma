from rest_framework import serializers


class GammaUsersSignupSourceSerializer(serializers.Serializer):
    """
    Serialize a signup source users data.
    """

    tenant = serializers.CharField()
    uids = serializers.ListField(child=serializers.CharField())
