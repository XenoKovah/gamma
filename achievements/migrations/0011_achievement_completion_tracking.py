from django.db import migrations, models
from django.db.models import Exists, OuterRef
from django.utils import timezone


def backfill_completed_achievements(apps, schema_editor):
    """
    Stamp achievements that are already complete as completed AND already seen.

    Pre-existing badges must not flood learners with "you earned a badge"
    notifications the first time they load a page after this feature deploys, so
    everything completed before the feature existed is marked seen at migration
    time. Only achievements completed after this migration produce notifications.

    An achievement is complete when it has no rule in a non-completed status —
    which also covers rule-less achievements (manual badge awards), matching
    Achievement.all_rules_completed (all([]) is True).
    """
    Achievement = apps.get_model('achievements', 'Achievement')
    AchievementRule = apps.get_model('achievements', 'AchievementRule')

    ts = timezone.now()
    incomplete_rules = AchievementRule.objects.filter(
        achievement=OuterRef('pk'),
    ).exclude(status='completed')

    Achievement.objects.annotate(
        has_incomplete_rules=Exists(incomplete_rules),
    ).filter(
        has_incomplete_rules=False,
    ).update(completed_at=ts, notification_seen_at=ts)


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0010_remove_achievementrule_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='completed_at',
            field=models.DateTimeField(blank=True, help_text='When the user completed this achievement. Unset for in-progress achievements and for achievements created by paths that bypass completion tracking (backfills).', null=True),
        ),
        migrations.AddField(
            model_name='achievement',
            name='notification_seen_at',
            field=models.DateTimeField(blank=True, help_text='When the "badge earned" notification for this achievement was shown to the user. A completed achievement with this unset is a pending notification.', null=True),
        ),
        migrations.RunPython(backfill_completed_achievements, migrations.RunPython.noop),
    ]
