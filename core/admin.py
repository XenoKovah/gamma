from django.contrib import admin

from core.models import AppClient


class AppClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'secret')


admin.site.register(AppClient, AppClientAdmin)
