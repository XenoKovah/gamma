from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.db import models
from django.http import HttpResponseForbidden
from django.utils.timezone import now

from rest_framework.permissions import IsAdminUser

from core.constants import ADMIN_PERMISSIONS_RESTRICTION


class AdminUserPermissionMixin:
    """
    Mixin to enforce admin permissions on create, update, and delete actions.
    """

    def get_permissions(self):
        """
        Apply admin permissions only for modification actions.
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


class TimestampModelMixin(models.Model):
    """
    Mixin for adding Timestamp.
    """

    created_at = models.DateTimeField(default=now, editable=False)

    class Meta:
        abstract = True


class AdminPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that restricts access to all except staff.

    Access rules:
        - Allowed: Users with `is_staff=True`.
        - Denied: Non-staff users (e.g., regular students).
        - Unauthenticated users are redirected to the login page.
        - Authenticated non-staff users receive a 403 Forbidden response.
    """

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url())
        return HttpResponseForbidden(ADMIN_PERMISSIONS_RESTRICTION)
