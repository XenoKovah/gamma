from django.urls import include, path
from rest_framework.routers import DefaultRouter

from avatar.api.v0.views import AvatarSetViewSet


router = DefaultRouter()
router.register('', AvatarSetViewSet)

urlpatterns = [
    path('avatar_set/', include(router.urls)),
]
