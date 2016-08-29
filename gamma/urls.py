"""gamma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.views import logout
from rest_framework.routers import SimpleRouter

from core.api import GameProfileView, ProgressView
from core.views import DashboardView


router = SimpleRouter()
router.register(r'game-profile', GameProfileView, base_name='game-profile')

urlpatterns = [
    url(r'^$', DashboardView.as_view()),
    url(r'^admin/', admin.site.urls),

    # Django Rest Framework
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Python Social Auth
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(
        r'^accounts/login/$',
        RedirectView.as_view(
            url=reverse_lazy('social:begin', args=['edx-oidc']),
            permanent=False,
            query_string=True
        ),
        name='login'
    ),
    url(r'^logout/$', logout, kwargs={'next_page': '/'}, name='logout'),

    url(r'^progress/(?P<pk>[0-9]+)/$', ProgressView.as_view(), name='progress'),
    url(r'^', include(router.urls)),
]
