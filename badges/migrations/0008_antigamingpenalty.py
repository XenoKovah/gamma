import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_gammauser_points'),
        ('badges', '0007_alter_badge_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='AntiGamingPenalty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.CharField(max_length=255)),
                ('points_docked', models.PositiveIntegerField(default=0)),
                ('rushed_blocks', models.PositiveIntegerField(default=0)),
                ('longest_run', models.PositiveIntegerField(default=0)),
                ('mode', models.CharField(default='flag', max_length=8)),
                ('evaluated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anti_gaming_penalties', to='users.gammauser')),
            ],
            options={
                'verbose_name': 'Anti-gaming penalty',
                'verbose_name_plural': 'Anti-gaming penalties',
                'unique_together': {('user', 'course_id')},
            },
        ),
    ]
