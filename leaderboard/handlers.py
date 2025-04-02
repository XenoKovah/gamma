from typing import Type

from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

from leaderboard import tasks
from users.models import GammaUser


@receiver(pre_save, sender=GammaUser)
def enqueue_leaderboards_user_data_update(sender: Type[GammaUser], instance: GammaUser, **kwargs) -> None:
    """
    Add user to the set of users whose leaderboards' data must be recalculated.

    Schedule the user's leaderboards' data update task only if the new Gamma
    user is created or the existed user points count is changed.
    """
    update_fields = kwargs["update_fields"] or ()

    if instance.pk and "points" not in update_fields:
        return

    transaction.on_commit(lambda: tasks.task_enqueue_leaderboards_user_data_update.delay(instance.user_uid))
