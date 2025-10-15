from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class UserEntity:
    id: int
    email: str
    role: Optional[str] = None
    hashed_password: Optional[str] = None
    provider: Optional[str] = None
    sub: Optional[str] = None

__all__ = ["UserEntity"]