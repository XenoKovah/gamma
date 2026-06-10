from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_remove_eventconfiguration_is_depends_on_achievement'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='block_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]
