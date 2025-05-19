from typing import Dict, List, Union

from core.base import UseCase
from users.models import GammaUser


class SignupSourceUpdateUseCase(UseCase):
    """
    Update users' signup source.

    The updated users count is returned.
    """

    def execute(self, data: Dict[str, Union[str, List[str]]]) -> int:
        return GammaUser.objects.filter(user_uid__in=data['uids']).update(signup_source=data['tenant'])
