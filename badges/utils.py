from typing import Optional

from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement
from badges.models import Badge


def is_achieved_badge(achievement: Achievement, course_id: Optional[str]) -> bool:
    """
    Check whether an achievement is an achieved badge.

    The badge is achieved if oll its rules are completed. If the course ID is
    provided, the badge must have at least one course-related rule.
    """
    badge_content_type = ContentType.objects.get_for_model(Badge)

    return (
        achievement.content_type == badge_content_type
        and achievement.all_rules_completed
        and (not course_id or achievement.get_course_related_achievement_rules(course_id))
    )
