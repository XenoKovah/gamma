import core.utils
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
            name='AppClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('key', models.CharField(db_index=True, default=core.utils.key_secret_generator, max_length=32, unique=True)),
                ('secret', models.CharField(default=core.utils.key_secret_generator, max_length=32, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GameProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('open_badges_id', models.CharField(blank=True, max_length=128)),
                ('points', models.IntegerField(default=0)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatar')),
                ('position', models.CharField(blank=True, max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
