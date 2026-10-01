from events.enums import EdxCommonEventTypes

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

# The only event types that anchor a ``completion_window`` (see
# RulesFilterService._window_anchor). The window measures how long a learner took to
# finish a class, from when they started it: their first "Mark as complete" click in
# the class (OST2 decision, 2026-10-01). Nothing else starts the clock: not watching a
# video, submitting an answer, bookmarking, forum activity or enrolling (passive — a
# learner may enroll and only begin months later), and not the certificate (the finish
# line). The bridge forwards only checks (``done: true``) and dedupes re-checks of a
# block, so every edx_done_toggled event is a real click. The backfilled history of
# the same clicks is the LMS's ``courseware_studentmodule`` rows of type ``done``.
WINDOW_ANCHOR_EVENT_TYPES = (
    EdxCommonEventTypes.EDX_DONE_TOGGLED.value,
)
