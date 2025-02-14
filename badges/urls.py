from django.urls import path, include

urlpatterns = [
    path('v0/', include('badges.api.v0.urls')),
]
