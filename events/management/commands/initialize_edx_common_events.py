from django.core.management.base import BaseCommand

from events.enums import EdxCommonEventTypes
from events.models import EventType, EventConfiguration


class Command(BaseCommand):
    """
    Management command for creating Event Types and Event Configurations.

    Create Event Types and Event Configurations according to common edX events.
    """

    help = 'Creates EventType and EventConfiguration entries for EdxCommonEventTypes enum.'

    def handle(self, *args, **options):
        for event in EdxCommonEventTypes:
            event_name = event.value
            title = event.title
            award = event.award

            event_type, created_type = EventType.objects.get_or_create(name=event_name)
            if created_type:
                self.stdout.write(self.style.SUCCESS(f'Created EventType: {event_name}'))
            else:
                self.stdout.write(f'EventType already exists: {event_name}')

            event_config, created_config = EventConfiguration.objects.get_or_create(
                event_type=event_type,
                defaults={
                    'title': title,
                    'award': award,
                }
            )
            if created_config:
                self.stdout.write(self.style.SUCCESS(f'Created EventConfiguration for: {title}'))
            else:
                self.stdout.write(f'EventConfiguration already exists: {title}')
