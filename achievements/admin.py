from django.contrib import admin

from achievements.models import Achievement, AchievementRule


class AchievementRuleInline(admin.TabularInline):
    model = AchievementRule
    extra = 1  # Number of empty rows to display
    fields = ('rule', 'status', 'created_at', 'actual_count', 'dependencies')
    readonly_fields = ('created_at',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'content_object')
    search_fields = ('user__username', 'content_type__model')
    inlines = [AchievementRuleInline]
