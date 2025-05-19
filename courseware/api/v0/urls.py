from django.urls import path

from courseware.api.v0 import views


urlpatterns = [
    path(r'courses/', views.CoursesView.as_view(), name='courses'),
    path(r'organizations/', views.OrganizationsView.as_view(), name='organizations'),
]
