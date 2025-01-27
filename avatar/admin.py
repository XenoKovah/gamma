from django.contrib import admin

from avatar.models import (
    AvatarBase,
    AvatarColor,
    AvatarItem,
    AvatarSet,
    AvatarSetItem,
    SkinType,
    UserAvatarConfig,
)


@admin.register(UserAvatarConfig)
class UserAvatarConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'avatar_set', 'use_avatar')
    list_filter = ('use_avatar', 'avatar_set')


@admin.register(AvatarSet)
class AvatarSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_image', 'avatar_color')
    filter_horizontal = ('avatar_items',)


@admin.register(AvatarItem)
class AvatarItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'skin_type')
    list_filter = ('skin_type',)


@admin.register(SkinType)
class SkinTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(AvatarColor)
class AvatarColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_color')


@admin.register(AvatarBase)
class AvatarBaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_image')


@admin.register(AvatarSetItem)
class AvatarSetItemAdmin(admin.ModelAdmin):
    list_display = ('avatar_base', 'avatar_item')
    list_filter = ('avatar_base', )
