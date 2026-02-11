import asyncio
from typing import Optional

from modules.shared.adapters import DomainService
from modules.shared.adapters.blob_storage import BlobStorageAdapter
from modules.shared.services.video.video_service import VideoService
from modules.video.entities.video_entity import VideoEntity
from modules.video.exceptions import VideoNotFoundException


class DownloadVideoDomainService(DomainService):
    def __init__(self, blob_storage: BlobStorageAdapter):
        super().__init__(DownloadVideoDomainService.__name__)
        self.__blob_storage = blob_storage

    async def process(self, user_id: str, video_id: str) -> Optional[VideoEntity]:
        self.logger.info(
            "Downloading video for user id " + user_id + " and video id " + video_id,
        )
        path = f"{user_id}/videos/{video_id}.mkv"
        if not await self.__blob_storage.exists(path):
            raise VideoNotFoundException(
                f"Video not found for user id {user_id} and video id {video_id}"
            )

        data = await self.__blob_storage.download_file(path)
        duration_seconds = await asyncio.to_thread(
            VideoService.get_video_duration_seconds,
            data,
        )

        return VideoEntity(
            user_id=user_id,
            video_id=video_id,
            data=data,
            size_bytes=len(data),
            duration_seconds=duration_seconds,
        )
