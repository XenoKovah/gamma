# Generated for the manual-badges feature (manual assignment criteria text).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0004_badge_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='manual_criteria',
            field=models.TextField(
                blank=True,
                default='',
                help_text=(
                    'For manually-assigned (rule-less) badges: free text describing how this badge is '
                    'granted. Shown to learners on hover, separately from the description.'
                ),
            ),
        ),
    ]
