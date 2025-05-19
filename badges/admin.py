from django.contrib import admin

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

    def rule_actions(self, obj):
        """
        Display the names of associated rules in the admin list view.
        """
        return ', '.join([str(rule.action) for rule in obj.rules.all()]) if obj.rules.exists() else 'No rules'


admin.site.register(Badge, BadgeAdmin)
