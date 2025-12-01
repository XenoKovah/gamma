"""
Base classes for achievements app.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Optional, Union

if TYPE_CHECKING:
    from avatars.models import Avatar
    from badges.models import Badge

logger = logging.getLogger(__name__)


class BaseProgressService(ABC):
    """
    Base class for progress services.
    """

    @abstractmethod
    def calculate_progress(self) -> Dict:
        """
        Calculate the current user's progress towards unlocking their achievement.
        """
        raise NotImplementedError

    @abstractmethod
    def resolve_current(self) -> Optional[Union[Badge, Avatar]]:
        """
        Resolve the current achievement target object.
        """
        raise NotImplementedError

    @abstractmethod
    def resolve_next(self, last_achieved: Optional[Union[Badge, Avatar]] = None) -> Optional[Union[Badge, Avatar]]:
        """
        Resolve the next achievement target object.
        """
        raise NotImplementedError
