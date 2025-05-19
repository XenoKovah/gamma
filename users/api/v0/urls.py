from django.urls import path

from users.api.v0.views import UserGameProfileView, SignupSourceUpdateView


urlpatterns = [
    path('users/gamma-profile/', UserGameProfileView.as_view(), name='user-gamma-profile'),
    path('users/update_profile_signup_source/', SignupSourceUpdateView.as_view(), name='update-profile-signup-source'),
]
