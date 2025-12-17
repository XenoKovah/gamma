from collections import OrderedDict

import pytest
from django.contrib.contenttypes.models import ContentType

from users.api.v0.serializers import UserGameProfileSerializer


@pytest.mark.django_db
class TestUserGameProfileSerializer:
    """
    Test Case for the testing UserGameProfileSerializer.
    """

    def test_serialized_data(
        self,
        avatar_factory,
        avatar_set_factory,
        gamma_user_factory,
        badge_factory,
        achievement_factory,
        user_avatar_config_factory,
    ):
        user = gamma_user_factory()
        badge = badge_factory()

        avatar_stage_1 = avatar_factory(stage=1)
        avatar_stage_2 = avatar_factory(stage=2)
        avatar_set = avatar_set_factory(is_draft=False, avatars=[avatar_stage_1, avatar_stage_2])
        user_avatar_config = user_avatar_config_factory(user=user, avatar_set=avatar_set)

        achievement_factory(
            user=user,
            content_type=ContentType.objects.get_for_model(type(badge)),
            object_id=badge.id,
            title=badge.title,
            description=badge.description,
        )

        expected_data = {
            'user_profile': {
                'id': user.id,
                'user_uid': user.user_uid,
                'username': user.username,
                'signup_source': user.signup_source,
            },
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
                             ('stage', avatar_stage_1.stage),
                             ('created_at', avatar_stage_1.created_at.isoformat().replace('+00:00', 'Z'))
                         ]),
                         OrderedDict([
                             ('id', avatar_stage_2.id),
                             ('title', avatar_stage_2.title),
                             ('description', avatar_stage_2.description),
                             ('image', avatar_stage_2.image.url),
                             ('rules', []),
                             ('stage', avatar_stage_2.stage),
                             ('created_at', avatar_stage_2.created_at.isoformat().replace('+00:00', 'Z'))
                         ])
                     ]),
                    ('is_draft', avatar_set.is_draft),
                    ('created_at', avatar_set.created_at.isoformat().replace('+00:00', 'Z'))
                ])
            ],
            'user_avatar_config': {
                'id': user_avatar_config.id,
                'user': user.id,
                'avatar_set': avatar_set.id,
                'avatar': OrderedDict([
                    ('id', avatar_stage_2.id),
                    ('title', avatar_stage_2.title),
                    ('description', avatar_stage_2.description),
                    ('image', avatar_stage_2.image.url),
                    ('rules', []),
                    ('stage', avatar_stage_2.stage),
                    ('created_at', avatar_stage_2.created_at.isoformat().replace('+00:00', 'Z'))
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
            'avatar_progress': {
                'current_points': user.points,
                'required_points': 0,
                'max_required_points': 0,
                'current_avatar': {
                    'id': avatar_stage_2.id,
                    'title': avatar_stage_2.title,
                    'stage': avatar_stage_2.stage,
                    'image': avatar_stage_2.image.url,
                    'description': avatar_stage_2.description,
                },
                'next_avatar': None,
            },
            'points': 100,
            'chart': {},
            'progress': {},
            'signup_source': None,
        }

        serializer = UserGameProfileSerializer(user)
        data = serializer.data

        assert expected_data == data
