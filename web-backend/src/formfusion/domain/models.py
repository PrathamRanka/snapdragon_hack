from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class SessionRecord:
    session_id: str
    join_code_digest: str
    exercise: str
    created_at: datetime
    expires_at: datetime
    devices: set[str] = field(default_factory=set)
    calibrated: bool = False

    @property
    def expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at
