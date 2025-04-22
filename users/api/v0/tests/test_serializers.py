from collections import OrderedDict

import pytest
from django.contrib.contenttypes.models import ContentType

from users.api.v0.serializers import UserGameProfileSerializer


@pytest.mark.django_db
class TestUserGameProfileSerializer:
    """
    Test Case for the testing UserGameProfileSerializer.
    """

    @pytest.mark.skip(reason='Temporarily skipped due to refactoring')
    def test_serialized_data(
        self,
        avatar_set_factory,
        gamma_user_factory,
        badge_factory,
        achievement_factory,
        user_avatar_config_factory,
    ):
        user = gamma_user_factory()
        badge = badge_factory()
        avatar_set = avatar_set_factory(is_draft=False)
        avatar_stage_1 = avatar_set.avatars.first()
        avatar_stage_2 = avatar_set.avatars.last()
        user_avatar_config = user_avatar_config_factory(user=user, avatar_set=avatar_set)

        achievement_factory(
            user=user,
            content_type=ContentType.objects.get_for_model(type(badge)),
            object_id=badge.id,
            title=badge.title,
            description=badge.description,
        )

        expected_data = {
            'avatar_sets': [
                OrderedDict([
                    ('id', avatar_set.id),
                    ('title', avatar_set.title),
                    ('avatars',
                     [
                         OrderedDict([
                             ('id', avatar_stage_1.id),
                             ('title', avatar_stage_1.title),
                             ('description', avatar_stage_1.description),
                             ('image', avatar_stage_1.image.url),
                             ('rules', []),
                             ('stage', None),
                             ('created_at', avatar_stage_1.created_at.isoformat().replace('+00:00', 'Z'))
                         ]),
                         OrderedDict([
                             ('id', avatar_stage_2.id),
                             ('title', avatar_stage_2.title),
                             ('description', avatar_stage_2.description),
                             ('image', avatar_stage_2.image.url),
                             ('rules', []),
                             ('stage', None),
                             ('created_at', avatar_stage_2.created_at.isoformat().replace('+00:00', 'Z'))
                         ])
                     ]),
                    ('use_in_courses', avatar_set.use_in_courses),
                    ('is_draft', avatar_set.is_draft),
                    ('created_at', avatar_set.created_at.isoformat().replace('+00:00', 'Z'))
                ])
            ],
            'user_avatar_config': {
                'id': user_avatar_config.id,
                'user': user.id,
                'avatar_set': avatar_set.id,
                'avatar': OrderedDict([
                    ('id', avatar_stage_1.id),
                    ('title', avatar_stage_1.title),
                    ('description', avatar_stage_1.description),
                    ('image', avatar_stage_1.image.url),
                    ('rules', []),
                    ('stage', None),
                    ('created_at', avatar_stage_1.created_at.isoformat().replace('+00:00', 'Z'))
                ]),
            },
            'system_badges': [
                OrderedDict([
                    ('id', badge.id),
                    ('title', badge.title),
                    ('description', badge.description),
                    ('image', badge.image.url),
                    ('is_active', badge.is_active),
                    ('slug', badge.slug),
                    ('rules', []),
                    ('created_at', badge.created_at.isoformat().replace('+00:00', 'Z'))
                ])
            ],
            'badges': [
                OrderedDict([
                    ('title', badge.title),
                    ('slug', badge.slug),
                    ('description', badge.description),
                    ('done', True),
                    ('progress', None),
                    ('object_id', badge.id),
                    ('object_uri', badge.image.url),
                    ('is_active', badge.is_active)
                ])
            ],
            'points': 100,
            'chart': {},
            'progress': {},
            'signup_source': None
        }

        serializer = UserGameProfileSerializer(user)
        data = serializer.data

        assert expected_data == data
