"""Service for importing Badges from CSV payloads."""

import csv
import logging
from pathlib import Path
from typing import Dict, List

from django.core.files import File

from badges.models import Badge

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ("slug", "image", "title")


class BadgeCSVImportService:
    """Service to import badges from a CSV file."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def run(self, csv_path: Path) -> None:
        logger.info(
            "Starting Badge CSV import path=%s dry_run=%s", csv_path, self.dry_run
        )
        for index, row in self._iterate_rows(csv_path):
            self._process_row(index, row)
        logger.info("Badge CSV import completed dry_run=%s", self.dry_run)

    def _iterate_rows(self, csv_path: Path) -> List[Dict[str, str]]:
        with csv_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            self._validate_header(reader.fieldnames or [])
            for line_no, row in enumerate(reader, start=2):
                yield line_no, row

    def _validate_header(self, header: List[str]) -> None:
        """Validate that the CSV header contains required columns."""
        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            raise ValueError(f"CSV file is missing required columns: {missing}")

    def _process_row(self, line_no: int, row: Dict[str, str]) -> None:
        """Process a single CSV row to create or update a Badge."""
        slug = (row.get("slug") or "").strip()
        image_path = Path((row.get("image") or "").strip())
        title = (row.get("title") or "").strip()

        if not slug or not title or not image_path:
            logger.warning("Skipping line %s: missing required data", line_no)
            return

        if not image_path.exists():
            logger.warning(
                "Skipping line %s: badge image does not exist (%s)", line_no, image_path
            )
            return

        defaults = {
            "title": title,
            "description": row.get("description", ""),
        }

        logger.info("Processing badge slug=%s", slug)

        if self.dry_run:
            logger.info("DRY-RUN: would create/update badge %s", slug)
            return

        with image_path.open("rb") as image_file:
            badge, created = Badge.objects.update_or_create(
                slug=slug,
                defaults={**defaults, "image": File(image_file, name=image_path.name)},
            )

        logger.info("%s badge %s", "Created" if created else "Updated", badge.slug)
