from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0011_achievement_completion_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='completion_points_paid',
            field=models.IntegerField(blank=True, help_text="How many of the source Badge's completion points were credited to the user for this achievement. Set by every path that pays them (the rule-driven completion use case, the manual grant, and the backfill command) so a payment can be audited and never repeated. NULL means \"no payment recorded\" — which for rows predating this field is not the same as \"never paid\", so the backfill command scopes itself with an explicit badge list and a completion cutoff rather than trusting NULL alone. 0 records a deliberate zero-point pay.", null=True),
        ),
    ]
