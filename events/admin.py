from django.contrib import admin
from events.models import Event, EventConfiguration, EventType
from events.forms import EventConfigurationForm


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(EventConfiguration)
class EventConfigurationAdmin(admin.ModelAdmin):
    # form = EventConfigurationForm
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
