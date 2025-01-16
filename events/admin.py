from django.contrib import admin

from events.models import Event, EventConfiguration, EventType


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Event model.
    """

    list_display = (
        'uid',
        'event_name',
        'username',
        'course_id',
        'client',
        'created_at'
    )
    list_filter = ('client', 'org', 'signup_source', 'created_at')
    search_fields = ('uid', 'username', 'course_id', 'client', 'org')
    readonly_fields = ('created_at',)

    def event_name(self, obj):
        return obj.configuration.event_name


@admin.register(EventConfiguration)
class EventConfigurationAdmin(admin.ModelAdmin):
    """
    Admin configuration for EventConfiguration model.
    """

    # TODO: the previous implementation used 'EventConfigurationForm' to create a new instance.
    list_display = ('event_type', 'title', 'award')
    search_fields = ('event_type__name', 'title')


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for EventType model.
    """

    list_display = ('name',)
    search_fields = ('name',)
