import pytest  # pylint: disable=import-error

from django.conf import settings
from django.contrib.admin.sites import AdminSite

from achievements.admin import StatusBadgeAdmin
from achievements.models import StatusBadge


@pytest.mark.django_db
def test_status_badge_view_on_site(make_test_file):
    store_relative_urls_default = settings.STORE_RELATIVE_URLS
    status_badge = StatusBadge(
        slug='my-title',
        title='My Title',
        status_points=10,
        badge_img=make_test_file())
    status_badge.save()
    status_badge_admin = StatusBadgeAdmin(StatusBadge, AdminSite())
    settings.STORE_RELATIVE_URLS = True
    assert status_badge_admin.view_on_site(status_badge).startswith('/')
    settings.STORE_RELATIVE_URLS = False
    assert status_badge_admin.view_on_site(status_badge).startswith('http')
    settings.STORE_RELATIVE_URLS = store_relative_urls_default
