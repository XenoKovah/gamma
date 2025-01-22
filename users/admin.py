from django.contrib import admin
from users.models import GammaUser


@admin.register(GammaUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Gamma User model.
    """

    list_display = ('username', 'user_uid', 'points')
