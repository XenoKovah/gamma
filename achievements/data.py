"""
Data classes for avatar application.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class AvatarProgressResult:
    current_points: int = 0
    required_points: int = 0
    current_avatar: Optional[Dict] = None
    next_avatar: Optional[Dict] = None
    max_required_points: int = 0
