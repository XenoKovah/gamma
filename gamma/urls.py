"""gamma URL Configuration.

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

from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.views.i18n import JavaScriptCatalog
from django.contrib import admin

from core.views import DashboardView, logout_view
from gamma.views import GammaView


urlpatterns = [
    # Dashboard page
    path('', DashboardView.as_view()),

    # Native admin page
    path('admin/', admin.site.urls),

    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # Django Rest Framework
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('logout/', logout_view, name='logout'),

    # API
    path('api/', include(('api.urls', 'api'), namespace='api')),

    path('badges/', TemplateView.as_view(template_name='badges.html')),

    path('api/', include('badges.urls')),
    path('api/', include('events.urls')),
    path('api/', include('avatars.urls')),
    path('api/', include('users.urls')),
    path('api/', include('leaderboard.urls')),

    # Gamma React routes
    path('gamma/<path:subpath>/', GammaView.as_view(), name='gamma_react_app'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
