from django import forms

from .models import Achievement


class AchievementForm(forms.ModelForm):
    """
    Form is intended to add extra field `rules`.

    `rules` field will be resposible for bagde rules saved in MongoDB.
    """
    rules = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(AchievementForm, self).__init__(*args, **kwargs)
        self.fields.get('rules').initial = 'Need to change to value from MongDB'

    class Meta:
        model = Achievement
        fields = '__all__'
