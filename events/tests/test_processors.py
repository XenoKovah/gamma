import pytest

from events.processors import CommonEventProcessor

pytestmark = pytest.mark.django_db

CERT_EVENT = 'edx_certificate_created'
COURSE_A = 'course-v1:org+A+1'
COURSE_B = 'course-v1:org+B+1'


@pytest.fixture
def cert_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name=CERT_EVENT)


def _make_cert_rule(rule_factory, configuration, course):
    return rule_factory(
        event_configuration=configuration,
        action={CERT_EVENT: {'count': 1}},
        filters={'course': course},
    )


def test_common_processor_counts_event_only_for_matching_course(
    cert_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    A certificate earned in one course must not progress a rule scoped to a different course.

    This guards the multi-course badge use case: a badge that holds one certificate rule per
    required course should only be granted once *all* of those courses have been certified,
    not after the first. Without the per-rule filter check a single certificate would progress
    every same-event-type rule on the badge.
    """
    user = gamma_user_factory()
    rule_b = _make_cert_rule(rule_factory, cert_configuration, COURSE_B)
    achievement_rule_b = achievement_rule_factory(rule=rule_b, dependencies={})

    processor = CommonEventProcessor()

    # Certificate in course A: the rule scoped to course B must NOT advance.
    event_a = event_factory(configuration=cert_configuration, course_id=COURSE_A, username=user.user_uid)
    dependencies_a = processor.process(achievement_rule_b, user, event_a)
    assert dependencies_a['is_achieved'] is False
    assert dependencies_a['events'][CERT_EVENT]['count'] == 0

    # Certificate in course B: the matching rule is now satisfied.
    event_b = event_factory(configuration=cert_configuration, course_id=COURSE_B, username=user.user_uid)
    dependencies_b = processor.process(achievement_rule_b, user, event_b)
    assert dependencies_b['is_achieved'] is True
    assert dependencies_b['events'][CERT_EVENT]['count'] == 1


def test_common_processor_counts_event_when_rule_has_no_course_filter(
    cert_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    A rule without a course filter still counts any matching event (no behaviour change).
    """
    user = gamma_user_factory()
    rule = rule_factory(
        event_configuration=cert_configuration,
        action={CERT_EVENT: {'count': 1}},
        filters={},
    )
    achievement_rule = achievement_rule_factory(rule=rule, dependencies={})

    event = event_factory(configuration=cert_configuration, course_id=COURSE_A, username=user.user_uid)
    dependencies = CommonEventProcessor().process(achievement_rule, user, event)

    assert dependencies['is_achieved'] is True
    assert dependencies['events'][CERT_EVENT]['count'] == 1
