from django.contrib import admin
from django.utils.html import format_html

from .forms import EventForm, StatusBadgeForm
from .models import Achievement, StatusBadge, Event


class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'get_badge_edit_url'
    )
    fields = (
        'title',
        'slug',
        'badge_img',
        'description',
    )
    prepopulated_fields = {"slug": ("title",)}

    def get_badge_edit_url(self, obj):
        return format_html('<a href="#/edit-rules/{}" class="js-no-click">Edit rules</a>', obj.slug)


class StatusBadgeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'status_points',
        'status_color'
    )
    fields = (
        'title',
        'slug',
        'badge_img',
        'description',
        'status_points',
        'status_color',
    )
    prepopulated_fields = {"slug": ("title",)}
    form = StatusBadgeForm


class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'award', 'title')
    exclude = ('color', 'notification_message')
    form = EventForm

    class Media:
        js = ("achievements/js/event.js",)

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(StatusBadge, StatusBadgeAdmin)
admin.site.register(Event, EventAdmin)
