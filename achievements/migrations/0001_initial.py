from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=64, unique=True)),
                ('badge_id', models.CharField(blank=True, max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('badge_img', models.ImageField(upload_to='media')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=64, unique=True)),
                ('title', models.CharField(blank=True, max_length=16)),
                ('award', models.PositiveSmallIntegerField(verbose_name='Points to award')),
                ('color', models.PositiveSmallIntegerField(choices=[(1, 'Applied Blue'), (2, 'Green'), (3, 'Yellow'), (4, 'Orange'), (5, 'Bright Blue'), (6, 'Purple'), (7, 'Light Gray'), (8, 'Red')], default=1)),
                ('notification_message', models.CharField(default='You have got {} point.', help_text="You can use {} to insert awarded points into correct place. e.g. Congrats! You've earned {} points for watching videos", max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='StatusBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=64, unique=True)),
                ('badge_id', models.CharField(blank=True, max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('status_points', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('status_color', models.CharField(blank=True, choices=[('blue', 'blue'), ('yellow', 'yellow'), ('red', 'red')], max_length=16)),
                ('badge_img', models.ImageField(upload_to='media')),
            ],
        ),
        migrations.CreateModel(
            name='UserStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='achievements.StatusBadge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='achievements.Achievement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
