"""
Downscaled copies of badge art, for the places that render badges as icons.

Why this exists
---------------
Badge source art is uploaded at full resolution -- on dev, 337 of the 438 images
are 1000x1000 and the heaviest are 1254x1254 at ~1 MB each -- while a leaderboard
row draws each badge at 84 CSS px. One leaderboard page therefore pulled tens of
megabytes of PNGs to paint icons a hundredth of that size.

``THUMBNAIL_MAX_SIZE`` is deliberately generous: 256 px still covers the rendered
size on a 3x-DPI screen, so the icons are pixel-for-pixel as good as before while
costing roughly an order of magnitude less to download.

The originals are never touched -- every badge keeps its full-resolution image for
surfaces that show it large, such as the per-badge leaderboard header.
"""
import logging
from io import BytesIO
from os import path

from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Long-edge cap, in pixels. Badge art is overwhelmingly square (417 of 438 images
# on dev are exactly 1:1), but ``Image.thumbnail`` preserves whatever ratio the
# source has, so the handful of wider badges scale correctly too.
THUMBNAIL_MAX_SIZE = (256, 256)

# PNG throughout: most badge art is flat-colour illustration that PNG compresses
# well, and -- unlike JPEG -- it keeps the alpha channel the icons are cut out
# with, which matters when they sit on a leaderboard row's background.
THUMBNAIL_FORMAT = 'PNG'
THUMBNAIL_SUFFIX = '.png'


def build_thumbnail(image_field, max_size=THUMBNAIL_MAX_SIZE):
    """
    Build a downscaled copy of ``image_field``.

    Returns a ``(filename, ContentFile)`` pair ready for ``ImageField.save()``, or
    ``None`` when there is nothing worth generating: no source file, a source that
    Pillow cannot read, or one already small enough to serve as its own icon.

    Never raises: a badge with unreadable art must not take down the leaderboard
    or abort a bulk regeneration, it should just keep serving its original image.
    """
    if not image_field or not getattr(image_field, 'name', None):
        return None

    try:
        # Read the source into memory first. Opening the FieldFile as a context
        # manager closes it on the way out, and handing Pillow the field directly
        # leaves whoever looks at the image next holding a closed handle.
        with image_field.open('rb') as source:
            raw = source.read()

        with Image.open(BytesIO(raw)) as img:
            img.load()

            if img.width <= max_size[0] and img.height <= max_size[1]:
                # Already icon-sized. A second copy would cost storage and a
                # cache entry while saving nobody any bytes.
                return None

            thumb = img.copy()
            thumb.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Palette and CMYK sources cannot be written straight to PNG with
            # their alpha intact; RGBA is the lossless common denominator.
            if thumb.mode not in ('RGBA', 'RGB', 'LA', 'L'):
                thumb = thumb.convert('RGBA')

            buffer = BytesIO()
            thumb.save(buffer, THUMBNAIL_FORMAT, optimize=True)
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError):
        logger.exception('Could not build a thumbnail for badge image %r', getattr(image_field, 'name', None))
        return None

    stem = path.splitext(path.basename(image_field.name))[0]
    return f'{stem}{THUMBNAIL_SUFFIX}', ContentFile(buffer.getvalue())
