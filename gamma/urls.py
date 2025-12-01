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

from auth_backends.urls import oauth2_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.views import DashboardView, logout_view
from gamma.views import GammaView


schema_view = get_schema_view(
   openapi.Info(
      title='Gamma API',
      default_version='v0',
      description='Gamma API documentation',
      license=openapi.License(name='BSD License'),
   ),
   public=True,
)

# Group swagger/openapi endpoints together for clarity and re-use
swagger_urlpatterns = [
    path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = oauth2_urlpatterns + [
    # Dashboard page (will be redirected to `/gamma/avatars/`)
    path('', DashboardView.as_view()),

    path('logout/', logout_view, name='logout'),

    # Native admin page
    path('admin/', admin.site.urls),

    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # Django Rest Framework
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('', include('avatars.urls')),
    path('', include('badges.urls')),
    path('', include('courseware.urls')),
    path('', include('events.urls')),
    path('', include('leaderboard.urls')),
    path('', include('users.urls')),

    # Gamma React routes
    path('gamma/<path:subpath>/', GammaView.as_view(), name='gamma_react_app'),
] + swagger_urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
