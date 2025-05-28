from enum import Enum

from django.utils.translation import ugettext_lazy as _

from core.mixins import EventTypeMixin


class RggInternalEventTypes(EventTypeMixin, Enum):
    """
    Enumeration of internal event types for the RGG system.
    """

    RGG_POINTS_DISTRIBUTION = ('rgg_points_distribution', _('Points Distribution'))
    RGG_ACHIEVEMENT_OBTAINED = ('rgg_achievement_obtained', _('Achievement Obtained'))


class EdxCommonEventTypes(EventTypeMixin, Enum):
    """
    Enumeration of Open edX common event types for the RGG system.
    """

    EDX_FORUM_TREAD_VOTED = ('edx_forum_thread_voted', _('Someone likes your Post'), 2)
    EDX_FORUM_THREAD_CREATED = ('edx_forum_thread_created', _('Add a Discussion Post'), 5)
    EDX_FORUM_RESPONSE_CREATED = ('edx_forum_response_created', _('Response to a Discussion Post'), 20)
    EDX_FORUM_COMMENT_CREATED = ('edx_forum_comment_created', _('Comment a Discussion Response'), 5)
    EDX_CERTIFICATE_CREATED = ('edx_certificate_created', _('Get a Course Certificate'), 50)
    EDX_GRADES_PROBLEM_SUBMITTED = ('edx_grades_problem_submitted', _('Submit an Answer'), 5)
    EDX_COURSE_ENROLLMENT_ACTIVATED = ('edx_course_enrollment_activated', _('Enroll in a Course'), 20)
    EDX_BOOKMARK_ADDED = ('edx_bookmark_added', _('Bookmark a Unit'), 1)
    EDX_STOP_VIDEO = ('stop_video', _('Watch a Video to the End'), 10)
