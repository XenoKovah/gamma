from rest_framework import authentication, exceptions

from core.models import AppClient


class KeySecretAuthentication(authentication.BaseAuthentication):
    """
    Authentication based in APP_KEY and APP_SECRET HEADERS.

    Client to pass "App-Key" and "App-Secret" in the header.
    """

    def authenticate(self, request):

        key = request.META.get('HTTP_APP_KEY')
        secret = request.META.get('HTTP_APP_SECRET')

        if not (key and secret):
            raise exceptions.AuthenticationFailed('Please provide APP_KEY and APP_SECRET')

        try:
            app_client = AppClient.objects.get(key=key, secret=secret)
        except AppClient.DoesNotExist:
            raise exceptions.AuthenticationFailed('Please provide a valid APP_KEY and APP_SECRET')

        # Adding client for event tracking
        request.client = app_client
