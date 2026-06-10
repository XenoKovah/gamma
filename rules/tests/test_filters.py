from datetime import timedelta

import pytest
from django.utils.timezone import now

from rules.constants import DATE_FORMAT, DATETIME_FORMAT
from rules.services import RulesFilterService

pytestmark = pytest.mark.django_db
mock_org = 'edx'
mock_course_id = f'course-v1:{mock_org}+1+1'
mock_event_name = 'stop_video'


@pytest.mark.parametrize(
    'start, end, org, course, expected_valid',
    [
        # Passed: Empty filters
        (
            None,
            None,
            None,
            None,
            True,
        ),
        # Passed: Valid interval, org, and course id match
        (
            (now() - timedelta(days=1)).strftime(DATETIME_FORMAT),
            (now() + timedelta(days=1)).strftime(DATETIME_FORMAT),
            mock_org,
            mock_course_id,
            True,
        ),
        # Passed: Interval is omitted
        (
            None,
            None,
            mock_org,
            mock_course_id,
            True,
        ),
        # Passed: Interval with provided only one field
        (
            None,
            (now() - timedelta(hours=1)).strftime(DATETIME_FORMAT),
            mock_org,
            mock_course_id,
            True,
        ),
        # Failed: Interval doesn't match
        (
            (now() - timedelta(days=1)).strftime(DATETIME_FORMAT),
            (now() - timedelta(hours=1)).strftime(DATETIME_FORMAT),
            mock_org,
            mock_course_id,
            False,
        ),
        # Failed: Interval incorrect format
        (
            (now() - timedelta(days=1)).strftime(DATE_FORMAT),
            (now() - timedelta(hours=1)).strftime(DATE_FORMAT),
            mock_org,
            mock_course_id,
            False,
        ),
        # Failed: Org mismatch
        (
            now().strftime(DATETIME_FORMAT),
            (now() + timedelta(hours=1)).strftime(DATETIME_FORMAT),
            'unknown',
            mock_course_id,
            False,
        ),
        # Failed: Course mismatch
        (
            now().strftime(DATETIME_FORMAT),
            (now() + timedelta(hours=1)).strftime(DATETIME_FORMAT),
            'unknown',
            'course-v1:unknown+2+2',
            False,
        ),
    ],
    ids=[
        'Passed: Empty filters',
        'Passed: Valid interval, org, and course id match',
        'Passed: Interval is omitted',
        'Passed: Interval with provided only one field',
        "Failed: Interval doesn't match",
        "Failed: Interval incorrect format",
        'Failed: Org mismatch',
        'Failed: Course mismatch',
    ]
)
def test_one_rule_based_on_filters_criteria(
    rule_factory,
    event_factory,
    event_configuration_factory,
    start,
    end,
    org,
    course,
    expected_valid,
):
    filters = {}

    if start or end:
        filters['interval'] = {}
        if start:
            filters['interval']['start'] = start
        if end:
            filters['interval']['end'] = end
    if org:
        filters['org'] = org
    if course:
        filters['course'] = course

    event_configuration = event_configuration_factory(event_type__name=mock_event_name)
    event = event_factory(configuration=event_configuration, org=mock_org, course_id=mock_course_id)
    rule = rule_factory(event_configuration=event_configuration, filters=filters, action={mock_event_name: 3})

    filtered_rules = RulesFilterService(event).filter_rules([rule])

    assert bool(filtered_rules) == expected_valid


@pytest.mark.parametrize(
    'action, expected_valid',
    [
        # Passed: Empty filters
        (
            {mock_event_name: 10},
            True,
        ),
        # Failed: Rules action mismatch
        (
            {'unknown_event_name': 10},
            False,
        ),
        # Failed: Action is empty
        (
            {},
            False,
        )
    ],
    ids=[
        'Passed: Relevant event in rules action',
        'Failed: Rules action mismatch',
        'Failed: Action is empty',
    ]
)
def test_one_rule_based_on_action_criteria(
    rule_factory,
    event_factory,
    event_configuration_factory,
    action,
    expected_valid,
):
    event_configuration = event_configuration_factory(event_type__name=mock_event_name)
    event = event_factory(configuration=event_configuration)
    rule = rule_factory(filters={}, action=action, event_configuration=event_configuration)

    filtered_rules = RulesFilterService(event).filter_rules([rule])

    assert bool(filtered_rules) == expected_valid


mock_block_a = 'block-v1:edx+1+1+type@done+block@aaaa'
mock_block_b = 'block-v1:edx+1+1+type@done+block@bbbb'


@pytest.mark.parametrize(
    'filter_blocks, event_block_id, expected_valid',
    [
        # Passed: No blocks filter matches any event block
        (None, mock_block_a, True),
        # Passed: Event block is in the filter list
        ([mock_block_a, mock_block_b], mock_block_a, True),
        # Passed: Single-string filter matches the event block
        (mock_block_a, mock_block_a, True),
        # Failed: Event block is outside the filter list
        ([mock_block_a], mock_block_b, False),
        # Failed: Single-string filter mismatch
        (mock_block_a, mock_block_b, False),
        # Failed: Pre-block_id event (NULL) never matches a blocks filter
        ([mock_block_a], None, False),
    ],
    ids=[
        'Passed: No blocks filter',
        'Passed: Block in list',
        'Passed: Single block string match',
        'Failed: Block outside list',
        'Failed: Single block string mismatch',
        'Failed: NULL block_id never matches',
    ]
)
def test_one_rule_based_on_blocks_filter(
    rule_factory,
    event_factory,
    event_configuration_factory,
    filter_blocks,
    event_block_id,
    expected_valid,
):
    filters = {} if filter_blocks is None else {'blocks': filter_blocks}

    event_configuration = event_configuration_factory(event_type__name=mock_event_name)
    event = event_factory(
        configuration=event_configuration,
        org=mock_org,
        course_id=mock_course_id,
        block_id=event_block_id,
    )
    rule = rule_factory(event_configuration=event_configuration, filters=filters, action={mock_event_name: 3})

    filtered_rules = RulesFilterService(event).filter_rules([rule])

    assert bool(filtered_rules) == expected_valid
