from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BadgeViewSet

router = DefaultRouter()
router.register('', BadgeViewSet)

urlpatterns = [
    path('badges/', include(router.urls)),
]
