import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ErrorDetail, ValidationError

from avatars.api.v0.serializers import AvatarSerializer, AvatarSetSerializer, Base64SVGField
from avatars.api.v0.tests.constants import BASE64_CORRECT_FILE, BASE64_INVALID_FILE
from avatars.constants import (
    AVATAR_SET_DUPLICATE_TITLE_ERROR,
    AVATAR_SET_TITLE_ERROR,
    AVATAR_STAGES_ERROR,
    AVATAR_TITLE_ERROR,
    INVALID_FILE_FORMAT,
    SVG_EXTENSION
)
from avatars.factories import AvatarFactory, AvatarSetFactory
from avatars.models import Avatar, AvatarSet
from events.factories import EventFactory, EventTypeFactory


@pytest.mark.django_db
class TestBase64SVGField:
    def setup_method(self):
        self.field = Base64SVGField()

    def test_valid_base64_svg(self):
        file = self.field.to_internal_value(BASE64_CORRECT_FILE)

        assert type(file) is SimpleUploadedFile
        assert file._name.endswith('.svg') is True

    def test_invalid_file_format(self):
        with pytest.raises(ValidationError, match=INVALID_FILE_FORMAT):
            self.field.to_internal_value(BASE64_INVALID_FILE)

    def test_valid_uploaded_file(self):
        uploaded_file = SimpleUploadedFile('test.svg', b'<svg></svg>', content_type='image/svg+xml')
        assert self.field.to_internal_value(uploaded_file) == uploaded_file


@pytest.mark.django_db
class TestAvatarSerializer:
    def test_valid_avatar(self):
        data = {
            'title': 'Test Avatar',
            'description': 'Test Description',
            'image': BASE64_CORRECT_FILE
        }

        serializer = AvatarSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        assert Avatar.objects.count() == 1
        assert Avatar.objects.first().title == 'Test Avatar'
        assert Avatar.objects.first().description == 'Test Description'

    def test_valid_avatar_only_update_rules(
        self,
        avatar_factory: AvatarFactory,
        event_configuration_factory: EventFactory,
        event_type_factory: EventTypeFactory
    ):
        avatar = avatar_factory()
        event_configuration_factory(event_type=event_type_factory(name='problem_check'))
        event_configuration_factory(event_type=event_type_factory(name='problem_graded'))
        data = {
            'title': 'single Avatar Title',
            'rules': [
                {
                    'action': {
                        'problem_check': 2
                    },
                    'filters': {
                        'interval': {
                            'start': '2012-12-20T12:20:12',
                            'end': '2020-12-20T12:20:12'
                        }
                    }
                },
                {
                    'action': {
                        'problem_graded': 4
                    },
                    'filters': {
                        'frequency': 2
                    }
                }
            ]
        }

        serializer = AvatarSerializer(instance=avatar, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        assert avatar.title == data['title']
        assert avatar.rules.count() == 2

        for i, rule in enumerate(avatar.rules.all()):
            assert rule.action == data['rules'][i]['action']
            assert rule.filters == data['rules'][i]['filters']

    def test_valid_avatar_update_all_fields(
            self,
            avatar_factory: AvatarFactory,
            event_configuration_factory: EventFactory,
            event_type_factory: EventTypeFactory
    ):
        avatar = avatar_factory()
        event_configuration_factory(event_type=event_type_factory(name='problem_check'))
        event_configuration_factory(event_type=event_type_factory(name='problem_graded'))
        data = {
            'title': 'single Avatar Title',
            'description': 'single Avatar Description',
            'image': BASE64_CORRECT_FILE,
            'rules': [
                {
                    'action': {
                        'problem_check': 2
                    },
                    'filters': {
                        'interval': {
                            'start': '2012-12-20T12:20:12',
                            'end': '2020-12-20T12:20:12'
                        }
                    }
                },
                {
                    'action': {
                        'problem_graded': 4
                    },
                    'filters': {
                        'frequency': 2
                    }
                }
            ]
        }

        serializer = AvatarSerializer(instance=avatar, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        assert avatar.title == data['title']
        assert avatar.description == data['description']
        assert avatar.rules.count() == 2

        for i, rule in enumerate(avatar.rules.all()):
            assert rule.action == data['rules'][i]['action']
            assert rule.filters == data['rules'][i]['filters']

    def test_missing_title(self):
        data = {
            'description': 'Test Description',
            'image': BASE64_CORRECT_FILE
        }
        serializer = AvatarSerializer(data=data)
        with pytest.raises(ValidationError, match=AVATAR_TITLE_ERROR):
            serializer.is_valid(raise_exception=True)

    def test_missing_image(self):
        data = {
            'title': 'Test Avatar',
            'description': 'Test Description'
        }

        expected_error_message = {'image': [ErrorDetail(string='No file was submitted.', code='required')]}

        serializer = AvatarSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

        assert serializer.errors == expected_error_message


@pytest.mark.django_db
class TestAvatarSetSerializer:
    def test_update_avatar_set_with_avatars(self, avatar_set_factory: AvatarFactory):
        avatar_set = avatar_set_factory(title='Test Avatar Set')
        data = {
            'avatars': [
                {
                    'title': 'Avatar 1',
                    'description': 'Avatar 1 description',
                    'image': BASE64_CORRECT_FILE
                },
                {
                    'title': 'Avatar 2',
                    'description': 'Avatar 2 description',
                    'image': BASE64_CORRECT_FILE
                }
            ]
        }

        serializer = AvatarSetSerializer(data=data)
        serializer.update(instance=avatar_set, validated_data=data)

        assert serializer.is_valid(), serializer.errors
        serializer.save()
        assert avatar_set.title == 'Test Avatar Set'
        assert avatar_set.avatars.count() == 2
        assert avatar_set.avatars.first().title == 'Avatar 1'
        assert avatar_set.avatars.last().title == 'Avatar 2'

    def test_update_avatar_set_requires_two_avatars(self, avatar_set_factory: AvatarSetFactory):
        avatar_set = avatar_set_factory()
        data = {
            'title': 'Test Avatar Set',
            'avatars': [
                {
                    'title': 'Only One Avatar',
                    'description': 'Not enough avatars',
                    'image': BASE64_CORRECT_FILE
                }
            ]
        }
        serializer = AvatarSetSerializer()
        with pytest.raises(ValidationError, match=AVATAR_STAGES_ERROR):
            serializer.update(instance=avatar_set, validated_data=data)
            serializer.is_valid(raise_exception=True)

    def test_title_validation(self, avatar_set_factory: AvatarSetFactory):
        avatar_set_factory(title='Test Avatar Set')
        data = {'title': 'Test Avatar Set'}

        serializer = AvatarSetSerializer(data=data)
        with pytest.raises(ValidationError, match=AVATAR_SET_DUPLICATE_TITLE_ERROR):
            serializer.is_valid(raise_exception=True)

        assert AvatarSet.objects.count() == 1

    def test_empty_title_validation(self):
        data = {'title': ''}

        serializer = AvatarSetSerializer(data=data)
        with pytest.raises(ValidationError, match=AVATAR_SET_TITLE_ERROR):
            serializer.is_valid(raise_exception=True)

        assert AvatarSet.objects.count() == 0
