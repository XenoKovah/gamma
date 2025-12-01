"""
Data classes for avatar application.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class AvatarProgressResult:
    current_points: int
    required_points: int
    current_avatar: Optional[Dict]
    next_avatar: Optional[Dict]
