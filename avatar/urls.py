from django.urls import include, path


urlpatterns = [
    path('v0/', include('avatar.api.v0.urls')),
]
