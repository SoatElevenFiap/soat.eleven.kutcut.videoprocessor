from typing import Optional

from pydantic import Field
from modules.shared.adapters import EntityAdapter


class VideoEntity(EntityAdapter):
    user_id: str
    video_id: str
    data: bytes
    size_bytes: int
    duration_seconds: int
    thumbnails_path: Optional[str] = Field(default=None)

    def set_thumbnails_path(self, thumbnails_path: str):
        self.thumbnails_path = thumbnails_path