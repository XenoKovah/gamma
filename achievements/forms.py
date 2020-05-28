import json

from django import forms

from edx_integration.api.v2.utils import get_gamma_events_list
from .models import Achievement, Event
from .services import AchievementRulesMongo

STORAGE = AchievementRulesMongo()


class AchievementForm(forms.ModelForm):
    """
    Form is intended to add extra field `rules`.

    `rules` field will be resposible for bagde rules saved in MongoDB.
    """
    rules = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(AchievementForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            STORAGE.connect()
            rules = json.dumps(STORAGE.get_rule(instance.slug))
            self.fields.get('rules').initial = rules

    def save(self, commit=True, *args, **kwargs):
        m = super(AchievementForm, self).save(commit=False)
        # TODO: Refactor this - need to move details update into form or some else util
        if self.cleaned_data.get('rules'):
            STORAGE.connect()
            STORAGE.upsert_rule(
                self.cleaned_data.get('slug'),
                self.cleaned_data.get('title'),
                json.loads(self.cleaned_data.get('rules'))
            )
        if commit:
            m.save()
        return m

    def clean_rules(self):
        """
        Validate input data to be convetable to JSON.
        """
        if self.cleaned_data['rules']:
            data = self.cleaned_data['rules']

            try:
                json_data = json.loads(data)
            except Exception:
                raise forms.ValidationError("Invalid data in rules field")

            return data

    class Meta:
        model = Achievement
        fields = ('id', 'title', 'badge_img', 'description')


class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['event_type'].widget.attrs['readonly'] = True
        else:
            events_list = get_gamma_events_list()
            if events_list:
                events_specified = Event.objects.all().values_list('event_type', flat=True)
                events_choices = (
                    (e['event_type'], e['event_type']) for e in events_list if e['event_type'] not in events_specified
                )
                self.fields['event_type'] = forms.ChoiceField(choices=events_choices)
                self.fields['event_type'].widget.attrs.update({
                    'data-event-names': json.dumps({
                        e['event_type']: e['verbose_name']
                        for e in events_list if e['event_type'] not in events_specified
                    })
                })

    def clean_event_type(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.event_type
        else:
            return self.cleaned_data['event_type']
