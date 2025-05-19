from django.urls import include, path

urlpatterns = [
    path('v0/', include(('courseware.api.v0.urls', 'courseware'),  namespace='v0')),
]
