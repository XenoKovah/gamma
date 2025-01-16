from django.urls import path, include

urlpatterns = [
    path('v0/', include('events.api.v0.urls')),
]
