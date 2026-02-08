from dataclasses import dataclass
from datetime import datetime


@dataclass
class IdempotencyKeyItem:
    """Ключ идемпотентности для саги."""
    key_type: str
    business_key: str
    id: int | None = None
    created_at: datetime | None = None
