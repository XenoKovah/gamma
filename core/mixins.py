from rest_framework.permissions import IsAdminUser


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
