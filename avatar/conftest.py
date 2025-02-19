import pytest_factoryboy

from avatar.factories import AvatarFactory, AvatarSetFactory


pytest_factoryboy.register(AvatarFactory)
pytest_factoryboy.register(AvatarSetFactory)
