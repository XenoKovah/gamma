from collections import OrderedDict

import pytest
from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement
from badges.models import Badge
from users.api.v0.serializers import UserGameProfileSerializer


@pytest.mark.django_db
class TestUserGameProfileSerializer:
    """
    Test Case for the testing UserGameProfileSerializer.
    """

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
                    ('category', badge.category),
                    ('image', badge.image.url),
                    ('is_active', badge.is_active),
                    ('slug', badge.slug),
                    ('points', badge.points),
                    ('manual_criteria', badge.manual_criteria),
                    ('excluded_categories', badge.excluded_categories),
                    ('rules', []),
                    ('created_at', badge.created_at.isoformat().replace('+00:00', 'Z'))
                ])
            ],
            'system_statuses': [],
            'badges': [
                OrderedDict([
                    ('title', badge.title),
                    ('slug', badge.slug),
                    ('description', badge.description),
                    ('done', True),
                    ('progress', None),
                    ('object_id', badge.id),
                    ('object_uri', badge.image.url),
                    ('is_active', badge.is_active),
                    ('points', badge.points)
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

    def test_deactivated_badges_hidden_but_achievements_kept(
        self, gamma_user_factory, badge_factory, achievement_factory,
    ):
        """
        A deactivated (draft) badge disappears from both system_badges and the
        user's earned-badge list, but its Achievement row is untouched -- so
        re-activating the badge restores it for everyone who earned it.
        """
        user = gamma_user_factory()
        active_badge = badge_factory(title='Active Badge')
        draft_badge = badge_factory(title='Speak at DEFCON', is_active=False)
        badge_content_type = ContentType.objects.get_for_model(Badge)
        for badge in (active_badge, draft_badge):
            achievement_factory(
                user=user,
                content_type=badge_content_type,
                object_id=badge.id,
                title=badge.title,
                description=badge.description,
            )

        data = UserGameProfileSerializer(user).data

        assert [badge['title'] for badge in data['system_badges']] == ['Active Badge']
        assert [badge['title'] for badge in data['badges']] == ['Active Badge']
        # The grant survives deactivation; only the display is suppressed.
        assert Achievement.objects.filter(
            user=user, content_type=badge_content_type, object_id=draft_badge.id,
        ).exists()

        draft_badge.is_active = True
        draft_badge.save(update_fields=('is_active',))
        data = UserGameProfileSerializer(user).data
        assert sorted(badge['title'] for badge in data['badges']) == ['Active Badge', 'Speak at DEFCON']

    def test_serialized_data_includes_active_system_statuses(self, gamma_user_factory, status_factory):
        """
        system_statuses returns only active statuses, ordered by threshold, in the
        shape the dashboard SliderStatusesBlock expects.
        """
        user = gamma_user_factory()
        status_factory(title='Bronze', status_points=100, is_active=True)
        status_factory(title='Gold', status_points=300, is_active=True)
        status_factory(title='Hidden', status_points=200, is_active=False)

        statuses = UserGameProfileSerializer(user).data['system_statuses']

        assert [s['status_points'] for s in statuses] == [100, 300]
        assert [s['title'] for s in statuses] == ['Bronze', 'Gold']
        assert set(statuses[0].keys()) == {
            'status_points', 'title', 'color', 'url', 'status_uid', 'active', 'slug',
        }
