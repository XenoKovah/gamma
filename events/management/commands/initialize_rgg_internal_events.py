from django.core.management.base import BaseCommand

from events.enums import RggInternalEventTypes
from events.models import EventType, EventConfiguration


class Command(BaseCommand):
    """
    Management command for create or update EventType and EventConfiguration
    entries for RggInternalEventTypes enum.
    """

    help = 'Creates EventType and EventConfiguration entries for RggInternalEventTypes enum.'

    def handle(self, *args, **options):
        for event in RggInternalEventTypes:
            event_name = event.value
            title = event.title

            event_type, created_type = EventType.objects.get_or_create(name=event_name)
            if created_type:
                self.stdout.write(self.style.SUCCESS(f'Created EventType: {event_name}'))
            else:
                self.stdout.write(f'EventType already exists: {event_name}')

            event_config, created_config = EventConfiguration.objects.update_or_create(
                event_type=event_type,
                defaults={
                    'title': title,
                    'award': 0,
                }
            )
            if created_config:
                self.stdout.write(self.style.SUCCESS(f'Created EventConfiguration for: {title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated EventConfiguration (award reset to 0) for: {title}'))
