from django.apps import AppConfig


class RulesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rules'

    def ready(self):
        import rules.signals  # pylint: disable=import-outside-toplevel, unused-import
