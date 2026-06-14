from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_gammausercoursepoints"),
    ]

    operations = [
        migrations.AddField(
            model_name="gammauser",
            name="excluded_from_leaderboard",
            field=models.BooleanField(default=False),
        ),
    ]
