from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import GameProfile, AppClient


class GameProfileInline(admin.StackedInline):
    model = GameProfile
    can_delete = False
    verbose_name_plural = 'GameProfile'
    fields = ['open_badges_id', 'points', 'avatar', 'position', 'id']


class UserAdmin(BaseUserAdmin):
    inlines = (GameProfileInline, )


class AppClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'secret')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(AppClient, AppClientAdmin)
admin.site.register(GameProfile)
