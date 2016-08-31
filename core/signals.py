from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_game_profile(sender, instance, created, **kwargs):
    if created:
        from core.models import GameProfile
        GameProfile.objects.create(
            user=instance
        )
