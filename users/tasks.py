from celery import shared_task

from users.continuous_learning import reset_stale_streaks


@shared_task
def reset_stale_continuous_learning_streaks() -> int:
    """
    Daily job: zero out Continuous Learning streaks broken by a missed day so their badge
    rings drop to 0% before the learner next earns points. Returns the number reset.
    """
    return reset_stale_streaks()
