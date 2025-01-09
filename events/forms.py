import json
from django import forms

from edx_integration.api.v2.utils import get_gamma_events_list
from events.models import EventConfiguration


class EventConfigurationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            self.fields['event_type'].widget.attrs['readonly'] = True
        else:
            events_choices, data_event_names =self.get_available_events()

            if all([events_choices, data_event_names]):
                self.fields['event_type'] = forms.ChoiceField(choices=events_choices)
                self.fields['event_type'].widget.attrs.update({'data-event-names': json.dumps(data_event_names)})

    def get_available_events(self):
        
        events_list = get_gamma_events_list()

        if not events_list:
            return None, None

        events_specified = EventConfiguration.objects.values_list('event_type', flat=True)

        events_choices = (
            (e['event_type'], e['event_type']) for e in events_list if e['event_type'] not in events_specified
        )
        data_event_names = {
            e['event_type']: e['verbose_name'] for e in events_list if e['event_type'] not in events_specified
        }
        return events_choices, data_event_names

    def clean_event_type(self):
        instance = getattr(self, 'instance', None)
        return instance.event_type if instance and instance.pk else self.cleaned_data['event_type']
