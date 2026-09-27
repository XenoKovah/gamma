"""
(Re)build the downscaled icon copy of every badge's art.

Why this exists
---------------
``Badge.save`` generates a thumbnail whenever a badge's image is set or swapped, so
badges uploaded from now on need nothing. The badges that already existed when the
``thumbnail`` field was added have none, and nobody is going to re-save 400-odd rows
by hand -- this command fills them in.

It is also the way to regenerate after a change to ``THUMBNAIL_MAX_SIZE``: run it
with ``--force`` and every badge is rebuilt at the new size.

Safety
------
* Only ever writes the derived ``thumbnail`` file/field. Source art is never touched,
  so the worst case of a bad run is wasted storage, fixable by running it again.
* Idempotent: without ``--force`` a badge that already has a thumbnail is skipped.
* ``--dry-run`` reports exactly what would change and writes nothing.
* One badge's unreadable art cannot abort the run -- ``build_thumbnail`` logs and
  returns ``None``, and that badge keeps serving its original image.
"""
from django.core.management.base import BaseCommand

from badges.models import Badge
from badges.thumbnails import THUMBNAIL_MAX_SIZE, build_thumbnail


class Command(BaseCommand):
    """
    Generate the thumbnail for every badge that does not have one.
    """

    help = "Generate downscaled thumbnails for badge images (used by the leaderboards)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Rebuild thumbnails that already exist (use after changing THUMBNAIL_MAX_SIZE).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would be generated, without writing anything.',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']

        badges = Badge.objects.exclude(image='').order_by('pk')
        total = badges.count()
        self.stdout.write(
            f'{total} badge(s) with art; thumbnail cap {THUMBNAIL_MAX_SIZE[0]}x{THUMBNAIL_MAX_SIZE[1]}px'
            + (' [DRY RUN]' if dry_run else '')
        )

        generated = skipped = unchanged = failed = 0
        source_bytes = thumb_bytes = 0

        for badge in badges.iterator():
            if badge.thumbnail and not force:
                skipped += 1
                continue

            try:
                original_size = badge.image.size
            except (OSError, ValueError):
                # The row points at a file that is not on disk.
                self.stderr.write(f'  ! badge {badge.pk} ({badge.title!r}): image file is missing')
                failed += 1
                continue

            if dry_run:
                built = build_thumbnail(badge.image)
                if built is None:
                    unchanged += 1
                    continue
                generated += 1
                source_bytes += original_size
                thumb_bytes += built[1].size
                continue

            if not badge.refresh_thumbnail():
                # Art unreadable or already icon-sized; it keeps serving the original.
                unchanged += 1
                continue

            generated += 1
            source_bytes += original_size
            try:
                thumb_bytes += badge.thumbnail.size
            except (OSError, ValueError):
                pass

        self.stdout.write(
            f'generated {generated}, already had one {skipped}, '
            f'left on the original {unchanged}, missing file {failed}'
        )
        if generated and source_bytes:
            saved = source_bytes - thumb_bytes
            self.stdout.write(
                f'icon payload for those {generated}: {source_bytes / 1048576:.1f} MB '
                f'-> {thumb_bytes / 1048576:.1f} MB ({saved * 100 // source_bytes}% smaller)'
            )
