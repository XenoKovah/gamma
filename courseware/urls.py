from django.urls import include, path


app_name = 'courseware'
urlpatterns = [
    path('api/', include(('courseware.api.urls', 'courseware'), namespace='api')),
]
