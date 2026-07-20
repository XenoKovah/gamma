"""
Deciding which learners count as "instructors" for leaderboard filtering.

Contributing class material is by far the largest source of points on the platform, so
instructors occupy the top of every board by construction. Every leaderboard therefore
offers a second view with them dropped, letting a learner see where they place among
their peers. This module is the single place that answers "who is an instructor".

An instructor is anyone holding an *earned* instructor badge, identified by its slug:
the flat ``instructor`` badge and the hour-scaled ``<N>h-instructor`` family
(``6h-instructor`` ... ``154h-instructor``). Matching the ``-instructor`` suffix rather
than a bare substring keeps unrelated slugs that merely end in those letters (say,
``constructor``) out of the set, while still picking up hour badges added later without
a code change.
"""
from typing import List, Optional, Set

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from achievements.models import Achievement
from badges.models import Badge

INSTRUCTOR_BADGE_SLUG = "instructor"
INSTRUCTOR_BADGE_SLUG_SUFFIX = f"-{INSTRUCTOR_BADGE_SLUG}"


def is_instructor_badge_slug(slug: Optional[str]) -> bool:
    """
    Whether ``slug`` names an instructor badge.
    """
    if not slug:
        return False
    return slug == INSTRUCTOR_BADGE_SLUG or slug.endswith(INSTRUCTOR_BADGE_SLUG_SUFFIX)


def get_instructor_badge_ids() -> List[int]:
    """
    Provide the ids of every instructor badge.

    Deactivated badges are deliberately included: hiding a badge stops it being
    displayed but the learner keeps the points it paid, so its holder still sits at
    the top of the board and still needs to be filterable.
    """
    return list(
        Badge.objects.filter(
            Q(slug=INSTRUCTOR_BADGE_SLUG) | Q(slug__endswith=INSTRUCTOR_BADGE_SLUG_SUFFIX)
        ).values_list("id", flat=True)
    )


def get_instructor_user_uids() -> Set[str]:
    """
    Provide the ``user_uid`` of everyone who has earned an instructor badge.

    Only earned achievements count — a learner part-way through an instructor badge's
    rules is not an instructor yet. Manual grants are rule-less, and ``all([])`` is
    ``True``, so they read as earned here exactly as they do everywhere else.

    This is resolved live on each request rather than cached: the badge set is a
    handful of rows and its holders a handful more, which is nothing against the rest
    of a leaderboard response, and it means a freshly granted instructor badge takes
    effect immediately instead of on a cache boundary.
    """
    badge_ids = get_instructor_badge_ids()
    if not badge_ids:
        return set()

    achievements = (
        Achievement.objects
        .filter(content_type=ContentType.objects.get_for_model(Badge), object_id__in=badge_ids)
        .select_related("user")
        .prefetch_related("achievement_rules")
    )
    return {
        achievement.user.user_uid
        for achievement in achievements
        if achievement.all_rules_completed
    }
