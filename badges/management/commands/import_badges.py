"""Management command to import badges from a CSV file."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser

from badges.services import BadgeCSVImportService


class Command(BaseCommand):
    """
    CLI entry for the badges importer.
    """

    help = """
    Import badges from a CSV file.

    CSV columns (comma separated):
        slug,image,title

    Field notes:
        slug    badge slug
        image   path to image
        title   badge title
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csv_path", type=Path, help="Absolute or relative path to the CSV payload.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and log actions without touching the database.",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete badges specified in the CSV by `slug`.",
        )

    def handle(self, *unused_args, **options):
        csv_path: Path = options["csv_path"].expanduser().resolve()
        dry_run: bool = options["dry_run"]
        delete: bool = options["delete"]

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        import_service = BadgeCSVImportService(dry_run=dry_run, delete=delete)
        import_service.run(csv_path)
