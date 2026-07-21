from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_gammauser_points"),
    ]

    operations = [
        migrations.AddField(
            model_name="gammauser",
            name="current_weekday_streak",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="gammauser",
            name="last_weekday_active_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
