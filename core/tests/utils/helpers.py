import string
import random

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


def get_authenticated_api_client(is_staff=False):
    """
    Returns api_client based on the is_staff parameter to make test requests.
    """
    api_client = APIClient()
    chars = string.ascii_lowercase
    username = ''.join(random.choice(chars) for _ in range(10))
    user = get_user_model().objects.create_user(username, f'{username}@example.com')
    if is_staff:
        user.is_staff = True
        user.save()

    api_client.force_authenticate(user=user)

    return api_client
