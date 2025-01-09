from django.contrib import admin
from users.models import GammaUser


@admin.register(GammaUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass
