from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0011_badge_validity_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='is_expiring',
            field=models.BooleanField(default=False, help_text='Whether grants of this badge can carry a per-user expiry date. Only expiring badges show the "Manage expiry" controls in the settings page and accept an expiry through the API. Set it when creating a badge meant to lapse (e.g. a recurring-donor badge); a badge already awarded without expiry dates is deliberately not converted -- create a new expiring badge and copy the holders across instead.'),
        ),
    ]
