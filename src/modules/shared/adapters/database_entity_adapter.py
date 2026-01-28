from datetime import UTC, datetime
from typing import Optional

from pydantic import Field
from modules.shared.adapters import EntityAdapter


class DatabaseEntityAdapter(EntityAdapter):
    id: Optional[str] = Field(default=None, serialization_alias="id", alias="_id")
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    def generate_created_at(self):
        self.created_at = datetime.now(UTC)

    def generate_updated_at(self):
        self.updated_at = datetime.now(UTC)