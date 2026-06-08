from django.contrib import admin, messages

from achievements.reconciliation import recompute_holders
from badges.models import Badge


class BadgeAdmin(admin.ModelAdmin):
    """
    Admin interface for the Badge model.
    """

    list_display = ('title', 'is_active', 'slug', 'rule_actions', 'id')
    search_fields = ('title', 'slug',)
    list_filter = ('is_active',)
    filter_horizontal = ('rules',)
    ordering = ('title',)
    actions = ('recompute_badge_holders',)

    def rule_actions(self, obj):
        """
        Display the names of associated rules in the admin list view.
        """
        return ', '.join([str(rule.action) for rule in obj.rules.all()]) if obj.rules.exists() else 'No rules'

    @admin.action(description='Recompute holders (grant/revoke under current rules)')
    def recompute_badge_holders(self, request, queryset):
        """
        Re-evaluate every selected badge against its current rules and grant/revoke accordingly.
        """
        for badge in queryset:
            result = recompute_holders(badge)
            self.message_user(request, f'{badge.title!r}: {result.summary()}', level=messages.SUCCESS)


admin.site.register(Badge, BadgeAdmin)
