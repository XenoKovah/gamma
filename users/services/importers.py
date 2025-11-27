"""Service helpers for importing Gamma entities from CSV sources."""

import csv
import logging
from collections import Counter
from pathlib import Path
from typing import List, Dict, Iterator, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.utils import IntegrityError

from achievements.models import Achievement, AchievementRule
from badges.models import Badge
from users.models import GammaUser, GammaUserCoursePoints
from events.models import EventType, EventConfiguration

from rules.models import Rule


logger = logging.getLogger(__name__)


EVENT_TYPE_NAME = "mock-eventtype"
BADGES_START_COLUMN = 3  # zero-based index


class CSVImportService:
    """Import Gamma users, course points, and badge achievements from CSV rows."""

    def __init__(self, *, dry_run: bool) -> None:
        self.dry_run = dry_run
        self.stats = Counter()
        self._badge_cache: Dict[str, Badge] = {}
        self._rule_cache: Dict[str, Rule] = {}
        self._badge_content_type = ContentType.objects.get_for_model(Badge)
        self._reader: Optional[csv.DictReader] = None

    def run(self, csv_path: Path) -> None:
        """Execute the CSV import routine."""
        logger.info("Starting Gamma CSV import path=%s dry_run=%s", csv_path, self.dry_run)
        for line_no, row in self._iterate_rows(csv_path):
            self._process_row(line_no, row)
        logger.info(
            "Import finished rows=%s users_created=%s users_updated=%s course_links=%s badges_awarded=%s dry_run=%s",
            self.stats["rows"],
            self.stats["users_created"],
            self.stats["users_updated"],
            self.stats["course_links"],
            self.stats["badges_awarded"],
            self.dry_run,
        )

    def _iterate_rows(self, csv_path: Path) -> Iterator[Tuple[int, Dict[str, str]]]:
        with csv_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
            self._reader = csv.DictReader(csv_file)
            badge_names = self._reader.fieldnames[BADGES_START_COLUMN:]
            try:
                self._validate_badge_names(badge_names)
            except ValueError as e:
                logger.error("Badge validation error: %s", e)
                return
            for line_no, row in enumerate(self._reader, start=2):  # 1=header
                yield line_no, row

    def _process_row(self, line_no: int, row: Dict[str, str]) -> None:
        """Process a single row."""
        self.stats["rows"] += 1
        user_uid = (row.get("user_uid") or "").strip()
        course_id = (row.get("course_id") or "").strip()
        try:
            points = int(row.get("points", 0))
        except ValueError:
            logger.warning("Skipping line %s: invalid points value %r", line_no, row.get("points"))
            return

        if not user_uid:
            logger.warning("Skipping line %s: missing user_uid", line_no)
            return

        if self.dry_run:
            logger.info(
                "[DRY-RUN] would sync user=%s points=%s course_id=%s",
                user_uid,
                points,
                course_id,
            )
            return

        with transaction.atomic():
            try:
                user, created = GammaUser.objects.update_or_create(
                    user_uid=user_uid,
                    is_demo_user=True,
                    defaults={
                        "points": points,
                        "username": user_uid,
                    },
                )
            except IntegrityError:
                logger.warning(
                    "Skipping line %s: could not create/update user_uid=%s. This user marked as is_demo_user=False",
                    line_no,
                    user_uid,
                )
                return

            self.stats["users_created" if created else "users_updated"] += 1

            if course_id:
                _, course_created = GammaUserCoursePoints.objects.update_or_create(
                    gamma_user=user,
                    course_id=course_id,
                    defaults={"points": points},
                )
                if course_created:
                    self.stats["course_links"] += 1

            self.stats["badges_awarded"] += self._sync_badges(user, row, course_id)

    def _validate_badge_names(self, badge_names: List[str]) -> List[str]:
        """Ensure all badge names from CSV exist in the database."""
        found_badges = Badge.objects.filter(title__in=badge_names).values_list("title", flat=True)
        if found_badges.count() != len(badge_names):
            missing = set(badge_names) - set(found_badges)
            raise ValueError(f"The following badges are missing in the database: {', '.join(missing)}")
        return badge_names

    def _sync_badges(self, user: GammaUser, row: Dict[str, str], course_id: Optional[str]) -> int:
        """Assign badges marked in the CSV row to the user."""
        awarded = 0
        for badge_name in self._reader.fieldnames[BADGES_START_COLUMN:]:
            raw_value = row.get(badge_name)
            if raw_value in (None, ""):
                continue

            try:
                should_assign = int(raw_value) > 0
            except ValueError:
                logger.warning(
                    "Badge column %s has non-integer value %r. Skipping.",
                    badge_name,
                    raw_value,
                )
                continue

            badge = self._get_badge(badge_name)

            if not badge:
                logger.warning("Badge %s not found. Skipping user %s.", badge_name, user.user_uid)
                continue

            if not should_assign:
                # Is value explicitly, 0 then remove the achievement if it exists
                achievements = Achievement.objects.filter(object_id=badge.id, user=user)
                achievements.delete()
                continue

            achievement, created = Achievement.objects.get_or_create(
                user=user,
                content_type=self._badge_content_type,
                object_id=badge.id,
                defaults={
                    "title": badge.title or badge_name,
                    "description": badge.description,
                },
            )
            if created:
                awarded += 1

            if course_id:
                # If course_id provided, link achievement to course via AchievementRule
                # the course_id must equal the rule's filters `course`
                AchievementRule.objects.get_or_create(
                    status="completed",
                    achievement=achievement,
                    rule=self._get_rule(course_id),
                    defaults={"dependencies": {"is_achieved": True}},
                )
            else:
                AchievementRule.objects.filter(achievement=achievement).delete()

        return awarded

    def _get_badge(self, badge_name: str) -> Optional[Badge]:
        """Fetch badge instance by title with basic caching."""
        cache_key = badge_name
        if cache_key not in self._badge_cache:
            self._badge_cache[cache_key] = Badge.objects.filter(title__iexact=badge_name).first()
        return self._badge_cache[cache_key]

    def _get_rule(self, course_id: str) -> Rule:
        """Fetch or create a Rule instance for the given course_id with caching."""
        if course_id not in self._rule_cache:
            eventtype, _ = EventType.objects.get_or_create(name=EVENT_TYPE_NAME)
            eventtype_config, _ = EventConfiguration.objects.get_or_create(event_type=eventtype, defaults={"award": 0})
            rule, _ = Rule.objects.get_or_create(
                event_configuration=eventtype_config,
                action={EVENT_TYPE_NAME: {"count": 1}},
                filters={"course": course_id},
            )
            self._rule_cache[course_id] = rule
            return rule
        return self._rule_cache[course_id]
