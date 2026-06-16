from django import forms
from django.contrib import admin, messages

from achievements.reconciliation import recompute_holders
from badges.models import Badge


class BadgeAdminForm(forms.ModelForm):
    """
    Badge admin form that mirrors the API's manual-only guard: negative points are
    only valid on a rule-less (manually-assigned) badge. In the admin the M2M
    ``rules`` is available in ``cleaned_data``, so the combined post-edit state can
    be checked here.
    """

    class Meta:
        model = Badge
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        points = cleaned_data.get('points')
        rules = cleaned_data.get('rules')
        if points is not None and points < 0 and rules:
            raise forms.ValidationError(
                'Negative points are only allowed on manually-assigned badges with no completion rules.'
            )
        return cleaned_data


class BadgeAdmin(admin.ModelAdmin):
    """
    Admin interface for the Badge model.
    """

    form = BadgeAdminForm
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
