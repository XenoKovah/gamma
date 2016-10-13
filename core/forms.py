from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import F

from django import forms

from .models import GameProfile, AppClient
from .services import MongoConnector
from .serializers import GameProfileSerializer
from .utils import key_secret_generator

from pointlog.models import LoggedEvent
from pointlog.tasks import check_user_achievements


class EventPointsForm(forms.Form):
    user_name = forms.CharField(max_length=64)
    points = forms.IntegerField(min_value=1)

    conn = MongoConnector()

    def save_event_points(self):
        user = self.cleaned_data['user_name']


        user = User.objects.filter(username=self.cleaned_data['user_name']).first()
        print 'user:', user, type(user)

        game_profile = GameProfile.objects.get(user=user)
        event_type = 'reward'
        award = self.cleaned_data['points']

        print 'points:', award, type(award)

        game_profile.points = F('points') + award
        # TODO try to avoid duplicate saving in Serializer
        game_profile.save()

        # TODO move this action to Celery
        # Update point value in mongo
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
        # TODO refactor this
        self.conn.find_one_and_update(
            filter_dict={
                'username': user.username
            },
            key=event_type,
            value=award,
            event_type='chart' #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        )

        game_profile = GameProfile.objects.get(user=user)
        serializer = GameProfileSerializer(game_profile)
        client, _ = AppClient.objects.get_or_create(name='reward')
        # Logging this event to prevent repeating
        log_event = LoggedEvent(
            uniq_id=key_secret_generator(),
            user=user,
            event_type=event_type,
            points=game_profile.points,
            client=client
        )
        log_event.save()

        if event_type == 'reward':
            check_user_achievements(user.id, event_type)
