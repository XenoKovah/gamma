from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0012_achievement_completion_points_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='expires_at',
            field=models.DateTimeField(blank=True, db_index=True, help_text='When this grant lapses. Unset (the default) means it never expires. Once past, the achievement is treated as not held on every learner-facing surface -- dashboard, profile, leaderboards, notifications -- but the row and the points already paid are kept, so renewing the grant (a later expires_at) restores it without paying the points twice.', null=True),
        ),
    ]
