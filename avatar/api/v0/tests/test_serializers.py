import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ErrorDetail, ValidationError

from avatar.api.v0.serializers import AvatarSerializer, AvatarSetSerializer, Base64SVGField
from avatar.api.v0.tests.constants import BASE64_CORRECT_FILE, BASE64_INVALID_FILE
from avatar.constants import (
    AVATAR_SET_DUPLICATE_TITLE_ERROR,
    AVATAR_SET_TITLE_ERROR,
    AVATAR_STAGES_ERROR,
    AVATAR_TITLE_ERROR,
    INVALID_FILE_FORMAT,
    SVG_EXTENSION
)
from avatar.factories import AvatarFactory, AvatarSetFactory
from avatar.models import Avatar, AvatarSet


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
            'avatar': [
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
        assert avatar_set.avatar.count() == 2
        assert avatar_set.avatar.first().title == 'Avatar 1'
        assert avatar_set.avatar.last().title == 'Avatar 2'

    def test_update_avatar_set_requires_two_avatars(self, avatar_set_factory: AvatarSetFactory):
        avatar_set = avatar_set_factory()
        data = {
            'title': 'Test Avatar Set',
            'avatar': [
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
