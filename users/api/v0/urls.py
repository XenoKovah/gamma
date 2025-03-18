from django.urls import path

from users.api.v0.views import UserGameProfileView


urlpatterns = [
    path('users/gamma-profile/', UserGameProfileView.as_view(), name='user-gamma-profile'),
]
