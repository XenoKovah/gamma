from django.conf import settings
from rest_framework import authentication, exceptions

from .models import AppClient


class KeySecretAuthentication(authentication.BaseAuthentication):
    """
    Authentication based in APP_KEY and APP_SECRET HEADERS.
    """
    def authenticate(self, request):
        if settings.DEBUG:
            return True

        app_key = request.META.get('HTTP_APP_KEY')
        app_secret = request.META.get('HTTP_APP_SECRET')

        try:
            app_client = AppClient.objects.get(key=app_key, secret=app_secret)
            # Adding client for event tracking
            request.client = app_client
        except AppClient.DoesNotExist:
            raise exceptions.AuthenticationFailed('Please provide APP_KEY and APP_SECRET')
