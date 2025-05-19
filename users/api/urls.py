from django.urls import include, path


urlpatterns = [
    path('v0/', include(('users.api.v0.urls', 'users'),  namespace='v0')),
]
