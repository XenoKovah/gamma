from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from filebrowser.settings import ADMIN_THUMBNAIL

from .models import Achievement, UserAchievement, StatusBadge, UserStatus, Event


class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'badge_id',
        'get_badge_edit_url'
    )
    fields = (
        'title',
        'slug',
        'badge_img',
        'badge_id',
        'description',
    )
    prepopulated_fields = {"slug": ("title",)}
    def get_badge_edit_url(self, obj):
        return format_html('<a href="#/{}" class="js-no-click">Edit rules</a>', obj.slug)
    
    class Media:
        css = {
            'all': ('core/css/stylesheet.css',)
        }


class StatusBadgeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'badge_id',
        'status_points',
        'status_color'
    )
    fields = (
        'title',
        'slug',
        'badge_img',
        'badge_id',
        'description',
        'status_points',
        'status_color',
    )
    prepopulated_fields = {"slug": ("title",)}


class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'award', 'title', 'color', 'notification_message')


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(StatusBadge, StatusBadgeAdmin)
# admin.site.register(UserAchievement, admin.ModelAdmin)
# admin.site.register(UserStatus, admin.ModelAdmin)
admin.site.register(Event, EventAdmin)
