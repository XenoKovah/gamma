import pytest

from rules.serializers import FiltersSerializer

# Pure serializer tests: no DB, so skip the autouse internal-events setup.
pytestmark = pytest.mark.no_rgg_events

BLOCK_A = 'block-v1:edx+C1+2026+type@done+block@aaaa'
BLOCK_B = 'block-v1:edx+C1+2026+type@done+block@bbbb'
BLOCK_OTHER_COURSE = 'block-v1:edx+C2+2025+type@done+block@cccc'


def validated(data):
    serializer = FiltersSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    return serializer.validated_data


def test_blocks_filter_accepts_single_string_as_list():
    assert validated({'blocks': BLOCK_A})['blocks'] == [BLOCK_A]


def test_blocks_filter_dedupes_and_sorts():
    assert validated({'blocks': [BLOCK_B, BLOCK_A, BLOCK_B]})['blocks'] == sorted([BLOCK_A, BLOCK_B])


@pytest.mark.parametrize(
    'bad',
    [[], [''], ['   '], ['block-v1:ok+1+1+type@done+block@x', 5], 5, {'usage': 'key'}],
    ids=['empty list', 'empty string', 'whitespace', 'mixed types', 'number', 'dict'],
)
def test_blocks_filter_rejects_invalid_values(bad):
    serializer = FiltersSerializer(data={'blocks': bad})
    assert not serializer.is_valid()
    assert 'blocks' in serializer.errors


def test_course_filter_derived_from_blocks():
    data = validated({'blocks': [BLOCK_A, BLOCK_B]})
    assert data['course'] == 'course-v1:edx+C1+2026'


def test_course_or_group_derived_from_cross_course_blocks():
    data = validated({'blocks': [BLOCK_A, BLOCK_OTHER_COURSE]})
    assert data['course'] == ['course-v1:edx+C1+2026', 'course-v1:edx+C2+2025']


def test_explicit_course_filter_not_overridden_by_derivation():
    data = validated({'blocks': [BLOCK_A], 'course': 'course-v1:edx+C9+1'})
    assert data['course'] == 'course-v1:edx+C9+1'


def test_unparseable_block_keys_derive_no_course():
    data = validated({'blocks': ['not-a-usage-key']})
    assert 'course' not in data


BLOCK_A_OLDER_VERSION = 'block-v1:edx+C1+2021+type@done+block@aaaa'


def test_blocks_filter_keeps_version_groups_sorted_and_deduped():
    """A group lists one unit in several versions of a class; it stays one entry."""
    data = validated({'blocks': [BLOCK_B, [BLOCK_A, BLOCK_A_OLDER_VERSION, BLOCK_A]]})
    assert data['blocks'] == [[BLOCK_A_OLDER_VERSION, BLOCK_A], BLOCK_B]


def test_blocks_filter_stores_a_one_key_group_as_its_plain_key():
    assert validated({'blocks': [[BLOCK_A], BLOCK_B]})['blocks'] == [BLOCK_A, BLOCK_B]


@pytest.mark.parametrize(
    'bad',
    [[[]], [[BLOCK_A, 5]], [[BLOCK_A, '  ']], [BLOCK_A, [BLOCK_A, BLOCK_A_OLDER_VERSION]]],
    ids=['empty group', 'non-string in group', 'blank in group', 'key in two entries'],
)
def test_blocks_filter_rejects_invalid_groups(bad):
    serializer = FiltersSerializer(data={'blocks': bad})
    assert not serializer.is_valid()
    assert 'blocks' in serializer.errors


def test_course_or_group_derived_from_every_class_version():
    data = validated({'blocks': [[BLOCK_A_OLDER_VERSION, BLOCK_A], BLOCK_B]})
    assert data['course'] == ['course-v1:edx+C1+2021', 'course-v1:edx+C1+2026']
