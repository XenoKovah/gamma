from django.contrib import admin
from django.utils.html import format_html
from .models import Achievement, UserAchievement


class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'show_image', 'badge_id', 'badge_type']

    def show_image(self, obj):
        return format_html('<img style="width:100px" src="{}" />', obj.badge_image.url)


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(UserAchievement, admin.ModelAdmin)
