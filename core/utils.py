from importlib import import_module

from django.conf import settings


def load_gamification_backend(backend_path, *args, **kwargs):
    module, klass = backend_path.rsplit('.', 1)
    module = import_module(module)
    return getattr(module, klass)(*args, **kwargs)


def get_gamification_backends():
    return [load_gamification_backend(backend_path) for backend_path in settings.GAMIFICATION_BACKENDS]
