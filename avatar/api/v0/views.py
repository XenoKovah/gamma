from rest_framework.views import APIView
from rest_framework.response import Response

from avatar.api.v0.serializers import AvatarColorSerializer, AvatarItemSerializer
from avatar.models import (
    AvatarBase,
    AvatarColor,
    AvatarItem,
    AvatarSet,
    AvatarSetItem,
    SkinType,
    UserAvatarConfig,
)


class AvatarItemsAPIView(APIView):
    """
    Temporary API endpoint to get avatar items.
    """

    def get(self, request, *args, **kwargs):
        colors = AvatarColor.objects.all()
        glasses = AvatarItem.objects.filter(skin_type__name='glasses')
        headdress = AvatarItem.objects.filter(skin_type__name='headdress')
        outerwear = AvatarItem.objects.filter(skin_type__name='outerwear')
        emotion = AvatarItem.objects.filter(skin_type__name='emotion')

        data = {
            'colors': AvatarColorSerializer(colors, many=True).data,
            'glasses': AvatarItemSerializer(glasses, many=True).data,
            'headdress': AvatarItemSerializer(headdress, many=True).data,
            'outerwear': AvatarItemSerializer(outerwear, many=True).data,
            'emotion': AvatarItemSerializer(emotion, many=True).data,
        }

        return Response(data)
