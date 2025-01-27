from rest_framework import serializers

from avatar.models import AvatarColor, AvatarItem


class AvatarColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvatarColor
        fields = ['id', 'name', 'hex_color']


class AvatarItemSerializer(serializers.ModelSerializer):
    skin_type = serializers.CharField(source='skin_type.name')

    class Meta:
        model = AvatarItem
        fields = ['id', 'name', 'skin_type', 'svg_file']
