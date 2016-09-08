import json

from django import forms

from .models import Achievement
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
            rules = json.dumps(STORAGE.get_rule(instance.slug))
            self.fields.get('rules').initial = rules

    def save(self, commit, *args, **kwargs):
        m = super(AchievementForm, self).save(commit=False)
        STORAGE.upsert_rule(
            self.cleaned_data.get('slug'),
            json.loads(self.cleaned_data.get('rules'))
        )
        if commit:
            m.save()
        return m

    def clean_rules(self):
        """
        Validate input data to be convetable to JSON.
        """
        data = self.cleaned_data['rules']

        try:
            json_data = json.loads(data)
        except Exception:
            raise forms.ValidationError("Invalid data in rules field")

        return data

    class Meta:
        model = Achievement
        fields = '__all__'
