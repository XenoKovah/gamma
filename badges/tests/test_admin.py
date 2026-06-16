import pytest
from django import forms

from badges.admin import BadgeAdminForm


pytestmark = pytest.mark.django_db


class TestBadgeAdminFormNegativePointsGuard:
    """
    The Badge admin form mirrors the API's manual-only guard: negative points are
    only valid on a rule-less (manually-assigned) badge. ``clean()`` checks the
    combined post-edit state, where the M2M ``rules`` is available.
    """

    def test_rejects_negative_points_with_rules(self, rule_factory):
        form = BadgeAdminForm()
        form.cleaned_data = {'points': -50, 'rules': [rule_factory()]}

        with pytest.raises(forms.ValidationError):
            form.clean()

    def test_allows_negative_points_without_rules(self):
        form = BadgeAdminForm()
        form.cleaned_data = {'points': -50, 'rules': []}

        assert form.clean() == {'points': -50, 'rules': []}
