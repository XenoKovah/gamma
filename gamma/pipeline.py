"""
Functions are typically used as oauth2 authorization pipeline step in `python-social-auth`.
"""

from social_core.pipeline.partial import partial


@partial
def ensure_user_is_synchronized(strategy, details, user=None, *_args, **_kwargs):
    """
    Synchronize user instance between LMS and Gamma from an OAuth2 provider with the Django user model.
    """
    if user:
        user.is_superuser = details.get('is_superuser', False)
        user.is_staff = details.get('is_staff', False)
        strategy.storage.user.changed(user)

    return {'user': user}
