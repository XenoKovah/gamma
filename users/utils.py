from django.contrib.contenttypes.models import ContentType

from avatars.models import Avatar
from achievements.models import Achievement


def get_received_user_avatars_ids(user_uid):
    """
    Get all received user's avatars ids.
    """
    content_type = ContentType.objects.get_for_model(Avatar)
    return list(Achievement.objects.filter(
        content_type=content_type, user__user_uid=user_uid
    ).values_list('object_id', flat=True))
