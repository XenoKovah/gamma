from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_remove_eventconfiguration_is_depends_on_achievement'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='event',
            index=models.Index(
                fields=['username', 'course_id', 'created_at'],
                name='event_user_course_time_idx',
            ),
        ),
    ]
