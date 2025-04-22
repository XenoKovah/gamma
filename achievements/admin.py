from django.contrib import admin

from achievements.models import Achievement, AchievementRule


class AchievementRuleInline(admin.TabularInline):
    model = AchievementRule
    extra = 1  # Number of empty rows to display
    fields = ('rule', 'status', 'created_at', 'dependencies', 'points')
    readonly_fields = ('created_at',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'content_object', 'all_rules_completed_status')
    search_fields = ('user__username', 'content_type__model')
    inlines = [AchievementRuleInline]

    def all_rules_completed_status(self, obj):
        """
        Display a human-readable status of whether all related rules are completed.
        """
        return 'Completed' if obj.all_rules_completed else 'In Progress'
    all_rules_completed_status.short_description = 'Rules Completion Status'
