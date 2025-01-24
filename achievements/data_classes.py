from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserAction:
    count: int = 0
    goal: int = None
    last: datetime = None

    def to_dict(self):
        return {
            'count': self.count,
            'goal': self.goal,
            'last': self.last.isoformat() if self.last else None,
        }
