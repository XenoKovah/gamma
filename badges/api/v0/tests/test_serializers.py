import pytest

from badges.api.v0.serializers import BadgeSerializer


pytestmark = pytest.mark.django_db


class TestBadgeSerializer:
    """
    The freeform ``category`` field is a plain CharField with no special handling,
    so it must round-trip transparently through the serializer in both directions.
    """

    def test_category_is_serialized(self, badge_factory):
        badge = badge_factory(category='Security')

        data = BadgeSerializer(badge).data

        assert 'category' in data
        assert data['category'] == 'Security'

    def test_category_defaults_to_blank_when_unset(self, badge_factory):
        badge = badge_factory()

        data = BadgeSerializer(badge).data

        assert data['category'] == ''

    def test_category_is_written_on_update(self, badge_factory):
        badge = badge_factory(category='')

        serializer = BadgeSerializer(badge, data={'category': 'Reverse Engineering'}, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        badge.refresh_from_db()
        assert badge.category == 'Reverse Engineering'


class TestBadgeSerializerNegativePointsGuard:
    """
    Negative points (a penalty) are only valid on a manually-assigned, rule-less
    badge — the serializer checks the combined post-edit state.
    """

    def test_rejects_negative_points_on_badge_with_rules(self, badge_factory, rule_factory):
        badge = badge_factory(set_rules=(rule_factory(),))

        serializer = BadgeSerializer(badge, data={'points': -50}, partial=True)

        assert not serializer.is_valid()
        assert 'points' in serializer.errors

    def test_allows_negative_points_on_ruleless_badge(self, badge_factory):
        badge = badge_factory()  # no rules

        serializer = BadgeSerializer(badge, data={'points': -50}, partial=True)

        assert serializer.is_valid(), serializer.errors
