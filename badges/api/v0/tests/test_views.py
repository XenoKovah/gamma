import pytest
from django.urls import reverse_lazy
from rest_framework import status


pytestmark = pytest.mark.django_db


class TestBadgeViewSet:

    def test_get_badge_list(self, client, badge_factory):
        badge_factory.create_batch(3)
        response = client.get(reverse_lazy('badge-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    def test_get_badge_list(self, client, badge_factory):
        badge = badge_factory()
        url = reverse_lazy('badge-detail', kwargs={'pk': badge.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': badge.id,
            'title': badge.title,
            'description': badge.description,
            'image': f'http://testserver/media/{badge.image}',
            'slug': badge.slug,
            'is_active': badge.is_active,
            'rules': [],
        }
