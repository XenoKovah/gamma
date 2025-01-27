from django.urls import path

from avatar.api.v0.views import AvatarItemsAPIView


urlpatterns = [
    path('v0/get_avatar_items/', AvatarItemsAPIView.as_view(), name='get_avatar_items'),
]
