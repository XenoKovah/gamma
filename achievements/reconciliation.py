"""
Recompute, from scratch, which users should hold an achievement (Badge or Avatar)
under its *current* rules — used by the manual "recompute now" action after a
template's rules are edited.

The event-driven pipeline only reacts to incoming events, so editing a live badge's
rules never re-evaluates existing holders (a tightened badge keeps its old holders;
a loosened one never back-fills). This module closes that gap: it evaluates every
candidate user's rule satisfaction from their stored ``Event`` history and reconciles
their ``Achievement``/``AchievementRule`` rows to match, granting newly-qualifying
users and revoking those who no longer qualify.

Revocation has no "un-obtain" event, so it cascades explicitly to achievements that
depend on the changed one via ``rgg_achievement_obtained`` (e.g. avatar evolution).
There are no points to unwind: badge completion only emits the 0-point internal
``rgg_achievement_obtained`` event; course points belong to the certificate events.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.timezone import make_aware, utc

from achievements.models import Achievement, AchievementRule
from achievements.usecases import AchievementCompletionUseCase
from events.enums import RggInternalEventTypes
from events.models import Event
from rules.constants import DATETIME_FORMAT
from rules.models import Rule
from users.models import GammaUser

logger = logging.getLogger(__name__)

ACHIEVEMENT_OBTAINED = RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value
DEPENDENT_TEMPLATE_MODELS = ('badges.Badge', 'avatars.Avatar')


@dataclass
class RecomputeResult:
    """
    Outcome of a recompute pass: which users were newly granted/revoked.
    """

    granted: List[str] = field(default_factory=list)
    revoked: List[str] = field(default_factory=list)
    unchanged: int = 0

    def record(self, outcome: str, user: GammaUser) -> None:
        if outcome == 'granted':
            self.granted.append(user.user_uid)
        elif outcome == 'revoked':
            self.revoked.append(user.user_uid)
        else:
            self.unchanged += 1

    def summary(self) -> str:
        return f'granted={len(self.granted)} revoked={len(self.revoked)} unchanged={self.unchanged}'


def recompute_holders(template) -> RecomputeResult:
    """
    Reconcile every candidate user for the given achievement template (Badge or Avatar).
    """
    service = AchievementReconciliationService()
    rules = list(template.rules.all())
    result = RecomputeResult()
    for user in _candidate_users(template, rules):
        result.record(service.reconcile_user(template, user), user)
    logger.info('Recomputed holders for %r: %s', template, result.summary())
    return result


def _content_type(template) -> ContentType:
    return ContentType.objects.get_for_model(type(template))


def _candidate_users(template, rules: List[Rule]) -> List[GammaUser]:
    """
    Current holders/in-progress users UNION users whose stored history matches any rule.
    """
    content_type = _content_type(template)
    user_uids: Set[str] = set(
        Achievement.objects
        .filter(content_type=content_type, object_id=template.id)
        .values_list('user__user_uid', flat=True)
    )
    for rule in rules:
        user_uids.update(_events_for_rule(rule).values_list('username', flat=True))

    return list(GammaUser.objects.filter(user_uid__in=user_uids))


def _event_name(rule: Rule) -> Optional[str]:
    configuration = rule.event_configuration
    return configuration.event_name if configuration else None


def _events_for_rule(rule: Rule):
    """
    Events (across all users) that count toward this rule, applying its filters.
    """
    name = _event_name(rule)
    if not name:
        return Event.objects.none()

    queryset = Event.objects.filter(configuration__event_type__name=name)
    filters = rule.filters or {}
    if course := filters.get('course'):
        queryset = queryset.filter(course_id=course)
    if org := filters.get('org'):
        queryset = queryset.filter(org=org)

    interval = filters.get('interval') or {}
    if start := _parse_datetime(interval.get('start')):
        queryset = queryset.filter(created_at__gte=start)
    if end := _parse_datetime(interval.get('end')):
        queryset = queryset.filter(created_at__lte=end)

    return queryset


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return make_aware(datetime.strptime(value, DATETIME_FORMAT), utc)
    except (ValueError, TypeError):
        return None


def _as_int(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _templates_depending_on(template) -> List:
    """
    Templates (Badge/Avatar) whose rules depend on ``template`` via rgg_achievement_obtained.
    """
    dependent_rules = Rule.objects.filter(
        event_configuration__event_type__name=ACHIEVEMENT_OBTAINED,
        action__rgg_achievement_obtained__dependent_object_id=template.id,
    )
    if not dependent_rules.exists():
        return []

    templates = []
    for label in DEPENDENT_TEMPLATE_MODELS:
        model = apps.get_model(label)
        templates.extend(model.objects.filter(rules__in=dependent_rules).distinct())
    return templates


class AchievementReconciliationService:
    """
    Reconcile a single user's Achievement for a template against its current rules.
    """

    MAX_CASCADE_DEPTH = 5

    def reconcile_user(
        self,
        template,
        user: GammaUser,
        visited: Optional[Set[Tuple[int, int]]] = None,
        depth: int = 0,
    ) -> str:
        """
        Reconcile ``user``'s Achievement for ``template``; return 'granted'/'revoked'/'unchanged'.
        """
        content_type = _content_type(template)
        visited = visited if visited is not None else set()
        key = (content_type.id, template.id)
        if key in visited or depth > self.MAX_CASCADE_DEPTH:
            return 'unchanged'
        visited.add(key)

        outcome = self._reconcile(template, user, content_type)

        # Revocation has no triggering event, so re-evaluate dependents (e.g. avatar evolution).
        if outcome == 'revoked':
            for dependent in _templates_depending_on(template):
                self.reconcile_user(dependent, user, visited=visited, depth=depth + 1)

        return outcome

    @transaction.atomic
    def _reconcile(self, template, user: GammaUser, content_type: ContentType) -> str:
        rules = list(template.rules.all())
        achievement = Achievement.objects.filter(
            content_type=content_type, object_id=template.id, user=user,
        ).first()
        was_earned = bool(achievement and achievement.all_rules_completed)

        satisfied = {rule.id: self._is_rule_satisfied(rule, user) for rule in rules}
        will_be_earned = bool(rules) and all(satisfied.values())

        # No progress at all under the current rules — drop a stale Achievement entirely.
        if not any(satisfied.values()) and not will_be_earned:
            if achievement:
                achievement.delete()
                return 'revoked' if was_earned else 'unchanged'
            return 'unchanged'

        if achievement is None:
            achievement = Achievement.objects.create(
                user=user,
                content_type=content_type,
                object_id=template.id,
                title=template.title,
                description=template.description,
            )
        self._sync_rules(achievement, rules, satisfied)

        if will_be_earned and not was_earned:
            # Reuse the normal completion path so grant-side effects (avatar evolution,
            # notifications) fire exactly as they would for an event-driven award.
            AchievementCompletionUseCase().execute(achievement)
            return 'granted'
        if was_earned and not will_be_earned:
            return 'revoked'
        return 'unchanged'

    def _is_rule_satisfied(self, rule: Rule, user: GammaUser) -> bool:
        """
        Whether the user satisfies a single rule, computed from stored history/state.
        """
        name = _event_name(rule)
        if not name:
            return False
        action_value = (rule.action or {}).get(name) or {}

        if 'count' in action_value:
            goal = _as_int(action_value.get('count'))
            # NOTE: the 'frequency' filter (consecutive-day reset) is not modelled here;
            # recompute counts all matching events. Exact for the common count==1 case.
            return goal is not None and _events_for_rule(rule).filter(username=user.user_uid).count() >= goal

        if 'points' in action_value:
            goal = _as_int(action_value.get('points'))
            return goal is not None and user.points >= goal

        if 'dependent_object_id' in action_value:
            dependent_object_id = action_value.get('dependent_object_id')
            # Satisfied only when the depended achievement is actually earned (all rules completed).
            return any(
                dependency.all_rules_completed
                for dependency in Achievement.objects
                .filter(user=user, object_id=dependent_object_id)
                .prefetch_related('achievement_rules')
            )

        return False

    @staticmethod
    def _sync_rules(achievement: Achievement, rules: List[Rule], satisfied: Dict[int, bool]) -> None:
        """
        Make the achievement's AchievementRule rows mirror the template's current rules.
        """
        rule_ids = {rule.id for rule in rules}
        achievement.achievement_rules.exclude(rule_id__in=rule_ids).delete()
        existing = {rule_link.rule_id: rule_link for rule_link in achievement.achievement_rules.all()}

        for rule in rules:
            status = (
                AchievementRule.Statuses.COMPLETED if satisfied[rule.id]
                else AchievementRule.Statuses.ACTIVE
            )
            rule_link = existing.get(rule.id)
            if rule_link is None:
                AchievementRule.objects.create(
                    achievement=achievement,
                    rule=rule,
                    status=status,
                    dependencies={'is_achieved': satisfied[rule.id]},
                )
            elif rule_link.status != status:
                rule_link.status = status
                rule_link.dependencies = {**(rule_link.dependencies or {}), 'is_achieved': satisfied[rule.id]}
                rule_link.save(update_fields=('status', 'dependencies'))
