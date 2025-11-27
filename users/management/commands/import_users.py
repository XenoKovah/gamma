"""Management command skeleton for importing Gamma entities from CSV."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser

from users.services import CSVImportService


class Command(BaseCommand):
    """CLI entry for the Gamma entities importer."""

    help = """
    Import Gamma users, badges, and related points from a CSV file.

    CSV columns (comma separated):
        user_uid,points,course_id,<badge_name1>,<badge_name_N>...

    Field notes:
        user_uid   Gamma User UID.
        points     Absolute number of points to assign.
        course_id  Optional course that should reflect the awards.
        badge_name Optional badge title (exact) to award; must already exist.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "csv_path", type=Path, help="Absolute or relative path to the CSV payload."
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and log actions without touching the database.",
        )

    def handle(self, *unused_args, **options):
        csv_path: Path = options["csv_path"].expanduser().resolve()
        dry_run: bool = options["dry_run"]

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        import_service = CSVImportService(dry_run=dry_run)
        import_service.run(csv_path)
