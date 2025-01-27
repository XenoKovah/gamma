from django.urls import include, path

from avatar.views import AvatarView


urlpatterns = [
    path('api/', include('avatar.api.v0.urls')),
    path('', AvatarView.as_view(), name='avatar_view'),
]
