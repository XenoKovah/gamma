from django.contrib import admin
from django.utils.html import format_html
from filebrowser.settings import ADMIN_THUMBNAIL

from .models import Achievement, UserAchievement
from .forms import AchievementForm


class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'show_badge_img',
        'badge_id',
        'status_badge',
        'status_points',
        'status_color'
    )
    fields = (
        'title',
        'slug',
        'badge_img',
        'badge_id',
        'description',
        'rules',
        'status_badge',
        'status_points',
        'status_color',
    )
    prepopulated_fields = {"slug": ("title",)}

    form = AchievementForm

    def show_badge_img(self, obj):
        return format_html(
            '<img style="width:100px" src="{}" />',
            obj.badge_img.version_generate(ADMIN_THUMBNAIL).url if obj.badge_img else None
        )


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(UserAchievement, admin.ModelAdmin)
