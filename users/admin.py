from django.contrib import admin
from users.models import GammaUser, GammaUserCoursePoints


@admin.register(GammaUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Gamma User model.
    """

    list_display = ('username', 'user_uid', 'points')


@admin.register(GammaUserCoursePoints)
class GammaUserCoursePointsAdmin(admin.ModelAdmin):
    """
    Admin configuration for the GammaUserCoursePoints model.
    """

    list_display = ('gamma_user', 'course_id', 'points')
    search_fields = ('course_id', 'gamma_user__user_uid')
