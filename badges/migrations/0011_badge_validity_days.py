from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0010_badge_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='validity_days',
            field=models.PositiveIntegerField(blank=True, help_text='Optional default lifetime, in days, of a grant of this badge. When set, a manual grant that does not name its own expiry lapses this many days after it is awarded (e.g. 365 for a yearly-donor badge). Leave blank for badges that never expire. A single grant can always override it: award_to_user(user, expires_at=...) -- e.g. a one-off $500 gift good for 5 years.', null=True),
        ),
    ]
