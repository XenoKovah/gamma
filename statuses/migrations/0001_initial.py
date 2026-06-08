# Hand-authored initial migration for the `statuses` app: re-adds the points-based
# status ladder that was removed during the RGG 4.0 rewrite. Run
# `python manage.py makemigrations statuses --check` in the gamma dev environment to
# confirm it matches the model before deploying.

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('status_points', models.PositiveIntegerField(
                    help_text='Points threshold a learner must reach to attain this status.')),
                ('color', models.CharField(blank=True, default='', max_length=32)),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/statuses/')),
                ('is_active', models.BooleanField(default=True)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Statuses',
                'ordering': ('status_points',),
            },
        ),
    ]
