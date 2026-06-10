from django.urls import path

from users.api.v0.views import (
    BadgeNotificationsSeenView,
    BadgeNotificationsView,
    SignupSourceUpdateView,
    UserGameProfileView,
)


urlpatterns = [
    path('users/gamma-profile/', UserGameProfileView.as_view(), name='user-gamma-profile'),
    path('users/badge-notifications/', BadgeNotificationsView.as_view(), name='user-badge-notifications'),
    path(
        'users/badge-notifications/seen/',
        BadgeNotificationsSeenView.as_view(),
        name='user-badge-notifications-seen',
    ),
    path('users/update_profile_signup_source/', SignupSourceUpdateView.as_view(), name='update-profile-signup-source'),
]
