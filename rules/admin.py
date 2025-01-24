from django.contrib import admin

from rules.models import Rule


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Rule model.
    """

    list_display = ('event_configuration', 'action', 'filters')
    list_filter = ('event_configuration',)
    search_fields = ('event_configuration__title', 'action', 'filters')
