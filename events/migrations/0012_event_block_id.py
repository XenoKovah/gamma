from django.db import migrations, models


class Migration(migrations.Migration):

    # Renumbered 0011 -> 0012 when this branch was rebased: gamma had meanwhile taken
    # 0011 for the (user, course, time) index. Both descended from 0010, which would
    # have left the app with two leaf migrations.
    dependencies = [
        ('events', '0011_event_user_course_time_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='block_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]
