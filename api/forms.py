from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import F
from django import forms

from .serializers import GameProfileSerializer

from core.models import GameProfile, AppClient
from core.services import MongoConnector
from core.utils import key_secret_generator
from pointlog.models import LoggedEvent
from pointlog.tasks import check_user_achievements


class EventPointsForm(forms.Form):
    username = forms.CharField(max_length=64)
    points = forms.IntegerField(min_value=1)

    conn = MongoConnector()

    def save_event_points(self):
        user = User.objects.filter(
            username=self.cleaned_data['username']
        ).first()
        event_type = 'reward'
        award = self.cleaned_data['points']

        game_profile = GameProfile.objects.get(user=user)
        game_profile.points = F('points') + award
        game_profile.save()

        self.conn.find_one_and_update(
            filter_dict={
                'date': datetime.strptime(
                    str(datetime.now().date()), '%Y-%m-%d'
                ),
                'username': user.username
            },
            key='points',
            value=award
        )
        self.conn.find_one_and_update(
            filter_dict={
                'username': user.username
            },
            key=event_type,
            value=award,
            event_type='chart'
        )

        game_profile = GameProfile.objects.get(user=user)
        serializer = GameProfileSerializer(game_profile)
        client, _ = AppClient.objects.get_or_create(name='reward')
        log_event = LoggedEvent(
            uniq_id=key_secret_generator(),
            user=user,
            event_type=event_type,
            points=game_profile.points,
            client=client,
            rewarded_points=award
        )
        log_event.save()

        if event_type == 'reward':
            check_user_achievements(user.id, event_type)
