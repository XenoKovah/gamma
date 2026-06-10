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
    EDX_DONE_TOGGLED = ('edx_done_toggled', _('Mark a Unit as Complete'), 5)
    EDX_STOP_VIDEO = ('stop_video', _('Watch a Video to the End'), 10)

    # Profile / account-settings milestones. These are derived from the Open edX
    # ``edx.user.settings.changed`` tracking event by the gamification bridge
    # (gamma_bridge.statements.profile.ProfileSettingStatement), which maps each
    # rewardable account/preference field onto one of the event names below.
    # Award values are starting points and can be tuned per EventConfiguration.
    EDX_PROFILE_NAME_MADE_PUBLIC = ('edx_profile_name_made_public', _('Make Your Name Public'), 10)
    EDX_PROFILE_IMAGE_ADDED = ('edx_profile_image_added', _('Add a Profile Picture'), 10)
    EDX_PROFILE_EDUCATION_SET = ('edx_profile_education_set', _('Add Your Education Level'), 5)
    EDX_PROFILE_LOCATION_SET = ('edx_profile_location_set', _('Add Your Location'), 5)
    EDX_PROFILE_LANGUAGE_SET = ('edx_profile_language_set', _('Add Your Primary Language'), 5)
    EDX_PROFILE_ABOUT_ME_SET = ('edx_profile_about_me_set', _('Write Your "About Me"'), 10)
