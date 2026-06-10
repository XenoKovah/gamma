from typing import Any, Type

from django.contrib.contenttypes.models import ContentType
from django.db import models

from achievements.models import Achievement, AchievementRule
from core.mixins import TimestampModelMixin
from events.models import EventConfiguration
from users.models import GammaUser


class RuleQuerySet(models.QuerySet):
    """
    Extend queryset manager with rule specific methods.
    """

    @staticmethod
    def _objects_with_pending_work(
        model: Type[models.Model], user: GammaUser, **extra_filters: Any
    ) -> models.QuerySet:
        """
        Content objects (badges/avatars) carrying the outer rule on which ``user``
        has not yet completed THIS rule's achievement instance.

        One Rule row can be attached to several badges/avatars (the settings UI
        deduplicates identical rule definitions), so completion must be judged
        per content object: the inner subquery correlates on both the candidate
        object (``object_id``) and the outer Rule (double ``OuterRef``).
        """
        completed_instance_for_object = AchievementRule.objects.filter(
            rule=models.OuterRef(models.OuterRef('pk')),
            status=AchievementRule.Statuses.COMPLETED,
            achievement__user=user,
            achievement__content_type=ContentType.objects.get_for_model(model),
            achievement__object_id=models.OuterRef('id'),
        )
        return (
            model.objects
            .filter(rules=models.OuterRef('pk'), **extra_filters)
            .exclude(models.Exists(completed_instance_for_object))
        )

    def not_completed_by_user(self, configuration: EventConfiguration, user: GammaUser) -> models.QuerySet['Rule']:
        """
        Rules with work left for this user on at least one object carrying them.

        A rule stays selected while ANY badge/avatar it is attached to lacks a
        completed achievement instance for the user. Judging completion on the
        bare (rule, user) pair starves shared rules: completing the rule under
        one object (e.g. an avatar) would permanently stop a badge sharing the
        same rule from ever starting. The object filters mirror what the
        backends process (active badges; avatars in non-draft sets), so rules
        attached only to inactive/draft objects are skipped rather than
        reprocessed on every event.
        """
        # Imported here: badges/avatars import the achievements app, which sits
        # alongside rules in several import chains — a module-level import would
        # be cycle-prone for no benefit.
        from avatars.models import Avatar
        from badges.models import Badge

        badges_with_pending_work = self._objects_with_pending_work(Badge, user, is_active=True)
        avatars_with_pending_work = self._objects_with_pending_work(Avatar, user, avatarset__is_draft=False)

        return (
            self.filter(event_configuration=configuration)
                .filter(
                    models.Q(models.Exists(badges_with_pending_work))
                    | models.Q(models.Exists(avatars_with_pending_work))
                )
        )


class Rule(TimestampModelMixin, models.Model):
    event_configuration = models.ForeignKey(
        'events.EventConfiguration',
        on_delete=models.CASCADE,
        related_name='rules',
        null=True,
    )
    action = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)

    objects = RuleQuerySet.as_manager()

    def __str__(self):
        return f'Rule for {self.action!r}'

    @property
    def is_event_type_relevant(self) -> bool:
        """
        Check if the rule applies to the given event based on event type.
        """
        return self.event_configuration.event_name in self.action

    @classmethod
    def ensure_rule_is_created_from_data(cls, rule_data):
        """
        Get existent or create new Rule from data.
        """
        if (rule := cls.objects.filter(**rule_data).first()) is None:
            rule = cls.objects.create(**rule_data)

        return rule

    def has_filter(self, name: str, value: Any) -> bool:
        """
        Check whether the rule has a filter with a specific value.

        A list-valued filter (e.g. several accepted courses) matches if ``value`` is one of them.
        """
        if name not in self.filters:
            return False
        stored = self.filters.get(name)
        if isinstance(stored, (list, tuple)):
            return value in stored
        return stored == value
