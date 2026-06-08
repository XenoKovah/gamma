from django.db import models
from django.utils.text import slugify

from core.mixins import TimestampModelMixin


class Status(TimestampModelMixin, models.Model):
    """
    A points-based status (a.k.a. level) on the learner's "Your Statuses" ladder.

    Statuses are global configuration: each one defines a points threshold that a
    learner reaches by accumulating points. Whether a given learner has *attained*
    a status is derived on the frontend by comparing the learner's points to
    ``status_points`` (see edx-gamma-dashboard SliderStatusesBlock), so no
    per-user state is stored here.

    This re-introduces the configurable status ladder that was dropped during the
    RGG 4.0 rewrite (formerly the ``StatusBadge`` model + ``core/db/statuses.py``).
    """

    title = models.CharField(max_length=255)
    status_points = models.PositiveIntegerField(
        help_text='Points threshold a learner must reach to attain this status.',
    )
    color = models.CharField(max_length=32, blank=True, default='')
    image = models.ImageField(upload_to='uploads/statuses/')
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'
        ordering = ('status_points',)

    def __str__(self):
        return f'Status {self.title!r} ({self.status_points} pts)'
