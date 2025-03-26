from django.contrib import admin

from avatars.models import Avatar, AvatarSet, UserAvatarConfig


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'rule_actions', 'stage', 'id')
    search_fields = ('title',)
    filter_horizontal = ('rules',)

    def rule_actions(self, obj):
        """
        Display the names of associated rules in the admin list view.
        """
        return ', '.join([str(rule.action) for rule in obj.rules.all()]) if obj.rules.exists() else 'No rules'


@admin.register(AvatarSet)
class AvatarSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_draft')
    search_fields = ('title',)
    filter_horizontal = ('avatars',)


@admin.register(UserAvatarConfig)
class UserAvatarConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'selected_avatar', 'avatar_set')
    search_fields = ('user__username',)
