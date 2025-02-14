from django.db import models
from django.utils.text import slugify


class Badge(models.Model):
    """
    Reward given to users for achieving specific conditions defined by rules.
    """

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='uploads/badges/')
    is_active = models.BooleanField(default=True)

    slug = models.SlugField(max_length=255, null=True, blank=True)
    rules = models.ManyToManyField('rules.Rule')

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'

    def __str__(self):
        rules = ', '.join(str(rule.action) for rule in self.rules.all()) if self.rules.exists() else 'No rules'
        return f'Badge {self.title!r} with rules {rules}'
