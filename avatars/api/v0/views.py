from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from achievements.models import Achievement
from avatars.api.v0.serializers import AvatarSetSerializer, AvatarSerializer
from avatars.constants import AVATAR_SET_FINISH_FAILURE, AVATAR_SET_FINISH_SUCCESS
from avatars.models import Avatar, AvatarSet
from core.mixins import AdminUserPermissionMixin


class AvatarSetViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    View set provides CRUD operations for managing Avatar Set.
    """

    queryset = AvatarSet.objects.all()
    serializer_class = AvatarSetSerializer

    def retrieve(self, request, pk=None):
        username = request.GET.get('username')
        result_dict = {}

        try:
            avatar_set = self.get_object()
            serializer = self.get_serializer(avatar_set)

            if username:
                avatar_content_type = ContentType.objects.get_for_model(Avatar)
                avatar_ids = list(avatar_set.avatars.values_list('id', flat=True))

                achievements = Achievement.objects.filter(
                    user__user_uid=username,
                    content_type=avatar_content_type,
                    object_id__in=avatar_ids
                )

                result_dict['achievements'] = {
                    'achieved_avatar_ids': list(achievements.values_list('object_id', flat=True))
                }

            result_dict.update(serializer.data)
            return Response(result_dict, status=status.HTTP_200_OK)
        except AvatarSet.DoesNotExist:
            return Response(
                {'detail': 'Avatar Set not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch'], url_path='finish')
    def finish_avatar_set(self, request, pk=None):
        """
        Custom action to update 'is_draft' to False.
        """
        avatar_set = self.get_object()

        if avatar_set.avatars.count() < 2:
            return Response(
                {'error': AVATAR_SET_FINISH_FAILURE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        avatar_set.is_draft = False
        avatar_set.save()

        return Response(
            {'message': AVATAR_SET_FINISH_SUCCESS},
            status=status.HTTP_200_OK,
        )


class AvatarViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    View set provides CRUD operations for managing single Avatar.
    """

    queryset = Avatar.objects.all().prefetch_related('rules')
    serializer_class = AvatarSerializer
