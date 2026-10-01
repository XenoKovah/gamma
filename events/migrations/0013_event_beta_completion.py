from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_event_block_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='beta_completion',
            field=models.BooleanField(default=False),
        ),
    ]
