from django.contrib import admin
from django.utils.html import format_html

from .models import Achievement, UserAchievement
from .forms import AchievementForm


class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'slug', 'show_image', 'badge_id', 'badge_type'
    )
    fields = (
        'title', 'slug', 'badge_image', 'badge_id', 'badge_type', 'description', 'rules'
    )
    prepopulated_fields = {"slug": ("title",)}

    form = AchievementForm

    def show_image(self, obj):
        return format_html('<img style="width:100px" src="{}" />', obj.badge_image.url)


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(UserAchievement, admin.ModelAdmin)
