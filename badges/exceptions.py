class BadgeExclusionError(Exception):
    """
    Raised when a badge cannot be granted because the learner holds a badge in one
    of its ``excluded_categories``.

    Carries the disqualifying badges so callers can tell the admin *why* the grant
    was refused rather than just that it failed.
    """

    def __init__(self, badge, blocking_badges):
        self.badge = badge
        self.blocking_badges = list(blocking_badges)
        titles = ', '.join(repr(b.title) for b in self.blocking_badges)
        super().__init__(
            f'{badge.title!r} cannot be granted: the learner holds {titles}, '
            f'which is in an excluded category.'
        )
