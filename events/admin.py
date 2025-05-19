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
        'created_at',
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

    list_display = ('event_type', 'title', 'award')
    search_fields = ('event_type__name', 'title')

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the form creation to exclude already used event types and set initial if exists.
        """
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['event_type'].queryset = EventType.objects.filter(configuration__isnull=True)
        else:
            form.base_fields['event_type'].initial = EventType.objects.get(id=obj.event_type.id)

        return form


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for EventType model.
    """

    list_display = ('name',)
    search_fields = ('name',)
