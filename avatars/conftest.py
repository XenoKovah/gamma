import pytest_factoryboy

from avatars.factories import AvatarFactory, AvatarSetFactory


pytest_factoryboy.register(AvatarFactory)
pytest_factoryboy.register(AvatarSetFactory)
