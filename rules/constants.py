from events.enums import EdxCommonEventTypes

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Event types that must NOT anchor a ``completion_window`` (see
# RulesFilterService._window_anchor). The window measures how long a learner took to
# finish a class, so it starts at their first real piece of work in it:
#   - the certificate is the finish line, not the start;
#   - enrolling is passive — a learner may enrol and only begin months later, and
#     anchoring there would punish them for a pace they never actually set.
# Everything else carrying a course id (marking units done, submitting answers,
# finishing videos, bookmarking, posting on the forum) counts as having started.
# Internal rgg_* events are anchored out implicitly: they are created without a
# course id, so the course-scoped lookup never sees them.
WINDOW_NON_ANCHOR_EVENT_TYPES = (
    EdxCommonEventTypes.EDX_CERTIFICATE_CREATED.value,
    EdxCommonEventTypes.EDX_COURSE_ENROLLMENT_ACTIVATED.value,
)
