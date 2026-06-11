# Generated for the all-badges page (free-text category for sorting badges).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0005_badge_manual_criteria'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='category',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Free-text grouping label for the badge. Used to sort badges on the all-badges page.',
                max_length=255,
            ),
        ),
    ]
