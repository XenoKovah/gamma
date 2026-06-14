from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_gammauser_excluded_from_leaderboard"),
    ]

    operations = [
        migrations.AddField(
            model_name="gammauser",
            name="current_streak",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="gammauser",
            name="last_active_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
