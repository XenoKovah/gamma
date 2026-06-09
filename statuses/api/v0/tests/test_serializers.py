import pytest

from statuses.api.v0.serializers import SystemStatusSerializer


@pytest.mark.django_db
class TestSystemStatusSerializer:
    """
    Tests for SystemStatusSerializer — the learner-facing shape consumed by the
    dashboard's SliderStatusesBlock.
    """

    def test_serialized_fields(self, status_factory):
        status = status_factory(title='Gold', status_points=220, color='gold', slug='gold')

        data = SystemStatusSerializer(status).data

        assert set(data.keys()) == {
            'status_points', 'title', 'color', 'url', 'status_uid', 'active', 'slug',
        }
        assert data['status_points'] == 220
        assert data['title'] == 'Gold'
        assert data['color'] == 'gold'
        assert data['slug'] == 'gold'
        assert data['status_uid'] == 'gold'        # source='slug'
        assert data['active'] is True              # source='is_active'
        assert data['url'] == status.image.url     # source='image'
