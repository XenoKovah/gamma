from django.urls import include, path
from rest_framework.routers import DefaultRouter

from avatars.api.v0.views import AvatarViewSet, AvatarSetViewSet, UserAvatarConfigViewSet


router = DefaultRouter()
router.register('avatar_set', AvatarSetViewSet, basename='avatar_set')
router.register('avatar', AvatarViewSet, basename='avatar')
router.register('user_avatar_config', UserAvatarConfigViewSet, basename='user_avatar_config')


urlpatterns = [
    path('', include(router.urls)),
]
