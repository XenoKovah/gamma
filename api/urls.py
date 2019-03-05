"""
Root API URLs.

All API URLs should be versioned, so urlpatterns should only
contain namespaces for the active versions of the API.
"""
from django.urls import path, include


urlpatterns = [
    path('v0/', include(('api.v0.urls', 'api'), namespace='v0')),
]
