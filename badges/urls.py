from django.urls import path, include

from rest_framework.routers import DefaultRouter
from badges.views import BadgeViewSet

router = DefaultRouter()
router.register('', BadgeViewSet)

urlpatterns = [
    path('badges/', include(router.urls)),
]
