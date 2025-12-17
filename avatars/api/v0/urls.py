from django.urls import include, path
from rest_framework.routers import DefaultRouter

from avatars.api.v0.views import AvatarProgressView, AvatarViewSet, AvatarSetViewSet, UserAvatarConfigViewSet


router = DefaultRouter()
router.register('avatar_set', AvatarSetViewSet, basename='avatar_set')
router.register('avatar', AvatarViewSet, basename='avatar')
router.register('user_avatar_config', UserAvatarConfigViewSet, basename='user_avatar_config')


urlpatterns = [
    path('avatar-progress/<str:username>/', AvatarProgressView.as_view(), name='avatar_progress'),
    path('', include(router.urls)),
]
