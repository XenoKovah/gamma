from django.urls import include, path


urlpatterns = [
    path('api/', include('avatar.api.v0.urls')),
]
