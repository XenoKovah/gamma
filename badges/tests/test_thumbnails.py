"""
Tests for badge thumbnails — the downscaled icon copies the leaderboards serve
instead of full-resolution badge art.
"""
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from badges.models import Badge
from badges.thumbnails import THUMBNAIL_MAX_SIZE, build_thumbnail

pytestmark = pytest.mark.django_db

OVERSIZED = (1000, 1000)


@pytest.fixture(autouse=True)
def isolated_media(settings, tmp_path):
    """
    Write badge art under the test's own tmp dir.

    MEDIA_ROOT defaults to ``<repo>/media``, and these tests deliberately save
    several images per case; without this they would litter the working tree.
    """
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


def _png(size, color=(10, 80, 200, 255)) -> bytes:
    """An RGBA PNG of the given size, like real badge art."""
    buffer = BytesIO()
    Image.new('RGBA', size, color).save(buffer, 'PNG')
    return buffer.getvalue()


def _upload(name='badge.png', size=OVERSIZED, color=(10, 80, 200, 255)) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, _png(size, color), content_type='image/png')


def _dimensions(image_field):
    with Image.open(BytesIO(_read(image_field))) as img:
        return img.size


def _read(image_field) -> bytes:
    """Read a stored field's bytes, whatever state its handle was left in."""
    with image_field.open('rb') as fh:
        return fh.read()


def test_saving_a_badge_generates_a_thumbnail(badge_factory):
    badge = badge_factory(image=_upload())

    assert badge.thumbnail, 'a badge with oversized art should get a thumbnail'
    assert max(_dimensions(badge.thumbnail)) == max(THUMBNAIL_MAX_SIZE)
    # The original is left untouched, for the surfaces that render badges large.
    assert _dimensions(badge.image) == OVERSIZED


def test_thumbnail_is_smaller_than_the_original(badge_factory):
    badge = badge_factory(image=_upload())

    assert badge.thumbnail.size < badge.image.size


def test_thumbnail_preserves_aspect_ratio(badge_factory):
    badge = badge_factory(image=_upload(size=(1600, 800)))

    width, height = _dimensions(badge.thumbnail)
    assert (width, height) == (256, 128)


def test_thumbnail_preserves_transparency(badge_factory):
    badge = badge_factory(image=_upload(color=(10, 80, 200, 0)))

    with Image.open(BytesIO(_read(badge.thumbnail))) as thumb:
        assert thumb.mode == 'RGBA'
        assert thumb.getpixel((0, 0))[3] == 0, 'alpha channel should survive the downscale'


def test_art_already_icon_sized_is_left_alone(badge_factory):
    """A small badge is its own icon; a second copy would save nobody any bytes."""
    badge = badge_factory(image=_upload(size=(64, 64)))

    assert not badge.thumbnail
    assert build_thumbnail(badge.image) is None


def test_replacing_the_image_regenerates_and_cleans_up(badge_factory):
    badge = badge_factory(image=_upload(name='first.png'))
    first_thumbnail = badge.thumbnail.name
    storage = badge.thumbnail.storage
    assert storage.exists(first_thumbnail)

    badge.image = _upload(name='second.png', size=(800, 400))
    badge.save()
    badge.refresh_from_db()

    assert badge.thumbnail.name != first_thumbnail
    assert _dimensions(badge.thumbnail) == (256, 128)
    assert not storage.exists(first_thumbnail), 'the superseded thumbnail should be deleted'


def test_resaving_without_touching_the_image_keeps_the_thumbnail(badge_factory):
    badge = badge_factory(image=_upload())
    original_thumbnail = badge.thumbnail.name

    badge.title = 'Renamed'
    badge.save()
    badge.refresh_from_db()

    assert badge.thumbnail.name == original_thumbnail


def test_unreadable_art_does_not_break_saving(badge_factory):
    """One corrupt upload must not take down the save path or the leaderboard."""
    badge = badge_factory(
        image=SimpleUploadedFile('broken.png', b'this is not a png', content_type='image/png'),
    )

    assert not badge.thumbnail
    assert Badge.objects.filter(pk=badge.pk).exists()
