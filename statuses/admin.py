from django.contrib import admin

from statuses.models import Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """
    Admin interface for configuring the point-based status ladder ("Your Statuses").

    This is the administrator configuration UI for status point thresholds: staff
    create/edit statuses here just as they manage Badges, Avatars and Rules.
    """

    list_display = ('title', 'status_points', 'is_active', 'slug', 'id')
    search_fields = ('title', 'slug')
    list_filter = ('is_active',)
    ordering = ('status_points',)
