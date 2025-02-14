from django.contrib import admin

from avatar.models import Avatar, AvatarSet, UserAvatarConfig


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)
    filter_horizontal = ('rules',)


@admin.register(AvatarSet)
class AvatarSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_draft')
    search_fields = ('title',)
    filter_horizontal = ('avatar',)


@admin.register(UserAvatarConfig)
class UserAvatarConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'selected_avatar', 'avatar_set')
    search_fields = ('user__username',)
