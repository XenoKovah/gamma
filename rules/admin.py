from django.contrib import admin
from rules.models import Rule


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    pass
