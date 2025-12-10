from typing import Type

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from achievements.tests.factories import AchievementFactory, AchievementRuleFactory
from badges.tests.factories import BadgeFactory
from core.tests.utils.helpers import load_params_from_json
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.serializers import LeaderboardMemberSerializer
from rules.tests.factories import RuleFactory
from users.tests.factories import GammaUserFactory


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
