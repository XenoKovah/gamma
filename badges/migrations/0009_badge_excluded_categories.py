# Generated for the badge-exclusion feature (categories that disqualify a learner).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0008_antigamingpenalty'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='excluded_categories',
            field=models.JSONField(
                default=list,
                blank=True,
                help_text=(
                    'Badge categories that disqualify a learner from this badge. If the learner already '
                    'holds any badge in any of these categories, granting this one is refused. Example: '
                    '["Ignominious!"] stops a learner flagged for gaming completions from being granted '
                    'an accomplishment badge.'
                ),
            ),
        ),
    ]
