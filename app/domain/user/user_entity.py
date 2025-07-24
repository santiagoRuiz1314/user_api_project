from datetime import datetime
from typing import Optional
from app.core.utils import string_utils, date_utils

class User:
    def __init__(self, id: str, email: str, password_hash: str,
                 is_active: bool = True,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.created_at = created_at or date_utils.get_current_utc()
        self.updated_at = updated_at or date_utils.get_current_utc()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "password_hash": self.password_hash,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            email=data["email"],
            password_hash=data["password_hash"],
            is_active=data.get("is_active", True),
            created_at=date_utils.parse_datetime(data.get("created_at")),
            updated_at=date_utils.parse_datetime(data.get("updated_at"))
        )

    @classmethod
    def create_new_user(cls, email: str, password_hash: str) -> "User":
        return cls(
            id=string_utils.generate_uuid(),
            email=email,
            password_hash=password_hash
        )

    def deactivate(self):
        self.is_active = False
        self.updated_at = date_utils.get_current_utc()

    def activate(self):
        self.is_active = True
        self.updated_at = date_utils.get_current_utc()
