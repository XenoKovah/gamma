from typing import Type

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from achievements.models import AchievementRule
from achievements.tests.factories import AchievementFactory, AchievementRuleFactory
from badges.factories import BadgeFactory
from badges.models import Badge
from core.tests.utils.helpers import load_params_from_json
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.serializers import LeaderboardMemberSerializer
from rules.factories import RuleFactory
from users.factories import GammaUserFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "entry",
    load_params_from_json("leaderboard/tests/resources/leaderboard_member_serializer_cases.json"),
)
def test_leaderboard_member_serializer_data_correctness(
    entry: dict,
    gamma_user_factory: Type[GammaUserFactory],
    achievement_factory: Type[AchievementFactory],
    achievement_rule_factory: Type[AchievementRuleFactory],
    badge_factory: Type[BadgeFactory],
    rule_factory: Type[RuleFactory],
) -> None:
    setup_data = entry["setup_data"]
    leaderboard_retrieving_context_data = setup_data["leaderboard_retrieving_context"]
    user_uid = leaderboard_retrieving_context_data["user_uid"]
    user_signup_source = leaderboard_retrieving_context_data["user_signup_source"]
    course_id = leaderboard_retrieving_context_data["course_id"]
    leaderboard_retrieving_context = LeaderboardRetrievingContext(user_uid, user_signup_source, course_id)

    user = gamma_user_factory(user_uid=user_uid, signup_source=user_signup_source)

    for badge_data in setup_data["badges"]:
        rules = [
            rule_factory(action=rule_data["action"], filters=rule_data["filters"])
            for rule_data in badge_data["rules"]
        ]
        badge = badge_factory(
            title=badge_data["title"],
            description=badge_data["description"],
            image=SimpleUploadedFile(
                name=badge_data["image_name"],
                content=b"dummy.content",
                content_type="image/png",
            ),
            set_rules=tuple(rules),
        )
        achievement = achievement_factory(
            user=user,
            content_type=ContentType.objects.get_for_model(type(badge)),
            object_id=badge.id,
            title=badge.title,
            description=badge.description,
        )

        for index, rule_data in enumerate(badge_data["rules"]):
            for achievement_rule_data in rule_data["achievement_rules"]:
                achievement_rule_factory(
                    achievement=achievement,
                    rule=rules[index],
                    dependencies=achievement_rule_data["dependencies"],
                    status=achievement_rule_data["status"],
                )

    serializer = LeaderboardMemberSerializer(
        user,
        context={"leaderboard_retrieving_context": leaderboard_retrieving_context},
    )

    assert serializer.data == entry["expected_serialization_result"]


@pytest.mark.django_db
def test_leaderboard_badge_title_follows_rename(
    gamma_user_factory: Type[GammaUserFactory],
    achievement_factory: Type[AchievementFactory],
    achievement_rule_factory: Type[AchievementRuleFactory],
    badge_factory: Type[BadgeFactory],
    rule_factory: Type[RuleFactory],
) -> None:
    """
    The hover title/description on the leaderboard reflect the badge's *current*
    name, not the stale snapshot copied onto the achievement when it was earned.
    """
    context = LeaderboardRetrievingContext("user-1", "main", None)
    user = gamma_user_factory(user_uid="user-1", signup_source="main")
    rule = rule_factory(action={"edx_bookmark_added": 1}, filters={})
    badge = badge_factory(
        title="Received a Post Like",
        description="Updated description.",
        image=SimpleUploadedFile(name="b.png", content=b"dummy.content", content_type="image/png"),
        set_rules=(rule,),
    )
    achievement = achievement_factory(
        user=user,
        content_type=ContentType.objects.get_for_model(type(badge)),
        object_id=badge.id,
        title="⑧ Received a Post Like",       # stale award-time snapshot
        description="Stale snapshot description.",
    )
    achievement_rule_factory(
        achievement=achievement,
        rule=rule,
        dependencies={},
        status=AchievementRule.Statuses.COMPLETED,
    )

    data = LeaderboardMemberSerializer(
        user,
        context={"leaderboard_retrieving_context": context},
    ).data

    assert len(data["badges"]) == 1
    assert data["badges"][0]["title"] == "Received a Post Like"
    assert data["badges"][0]["description"] == "Updated description."


@pytest.mark.django_db
def test_leaderboard_badges_ordered_by_points_desc(
    gamma_user_factory: Type[GammaUserFactory],
    achievement_factory: Type[AchievementFactory],
    achievement_rule_factory: Type[AchievementRuleFactory],
    badge_factory: Type[BadgeFactory],
    rule_factory: Type[RuleFactory],
) -> None:
    """
    A member's achieved badges are returned highest-value first (Badge.points
    descending), regardless of the order the achievements were earned.
    """
    context = LeaderboardRetrievingContext("user-ord", "main", None)
    user = gamma_user_factory(user_uid="user-ord", signup_source="main")
    content_type = ContentType.objects.get_for_model(Badge)

    # Created in a deliberately non-descending order to prove the sort runs.
    for title, points in [("Low", 10), ("High", 100), ("Mid", 50)]:
        rule = rule_factory(action={"edx_bookmark_added": 1}, filters={})
        badge = badge_factory(
            title=title,
            points=points,
            image=SimpleUploadedFile(name=f"{title}.png", content=b"dummy.content", content_type="image/png"),
            set_rules=(rule,),
        )
        achievement = achievement_factory(
            user=user, content_type=content_type, object_id=badge.id, title=title,
        )
        achievement_rule_factory(
            achievement=achievement, rule=rule, dependencies={},
            status=AchievementRule.Statuses.COMPLETED,
        )

    data = LeaderboardMemberSerializer(
        user, context={"leaderboard_retrieving_context": context},
    ).data

    assert [badge["title"] for badge in data["badges"]] == ["High", "Mid", "Low"]


@pytest.mark.django_db
def test_leaderboard_skips_dangling_badge_without_crashing(
    gamma_user_factory: Type[GammaUserFactory],
    achievement_factory: Type[AchievementFactory],
    achievement_rule_factory: Type[AchievementRuleFactory],
    badge_factory: Type[BadgeFactory],
    rule_factory: Type[RuleFactory],
) -> None:
    """
    A completed achievement whose Badge was deleted (content_object is None) is
    skipped rather than crashing the whole leaderboard response.
    """
    context = LeaderboardRetrievingContext("user-dangle", "main", None)
    user = gamma_user_factory(user_uid="user-dangle", signup_source="main")
    content_type = ContentType.objects.get_for_model(Badge)

    # A live badge the member has earned.
    live_rule = rule_factory(action={"edx_bookmark_added": 1}, filters={})
    live_badge = badge_factory(
        title="Live Badge", points=10,
        image=SimpleUploadedFile(name="live.png", content=b"dummy.content", content_type="image/png"),
        set_rules=(live_rule,),
    )
    live = achievement_factory(user=user, content_type=content_type, object_id=live_badge.id, title="Live Badge")
    achievement_rule_factory(
        achievement=live, rule=live_rule, dependencies={}, status=AchievementRule.Statuses.COMPLETED,
    )

    # A dangling achievement: Badge content type, but object_id points at no Badge.
    dangling_rule = rule_factory(action={"edx_bookmark_added": 1}, filters={})
    dangling = achievement_factory(user=user, content_type=content_type, object_id=999999, title="Deleted Badge")
    achievement_rule_factory(
        achievement=dangling, rule=dangling_rule, dependencies={}, status=AchievementRule.Statuses.COMPLETED,
    )

    data = LeaderboardMemberSerializer(
        user, context={"leaderboard_retrieving_context": context},
    ).data

    assert [badge["title"] for badge in data["badges"]] == ["Live Badge"]
