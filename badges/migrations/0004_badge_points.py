# Generated for the manual-badges feature.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0003_badge_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='points',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Points granted to a user when this badge is manually assigned to them by an admin.',
            ),
        ),
    ]
