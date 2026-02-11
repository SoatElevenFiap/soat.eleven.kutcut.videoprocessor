import asyncio
import io
import zipfile

from modules.shared.adapters import DomainService
from modules.shared.adapters.blob_storage import BlobStorageAdapter
from modules.shared.services.video.video_service import VideoService
from modules.video.entities.video_entity import VideoEntity


class GenerateSnapshotsDomainService(DomainService):
    def __init__(self, blob_storage: BlobStorageAdapter):
        super().__init__(GenerateSnapshotsDomainService.__name__)
        self.__blob_storage = blob_storage

    async def process(self, video: VideoEntity) -> VideoEntity:
        self.logger.info(
            "Generating snapshots for video id " + video.video_id
            + " (single-pass decode, may take a while for long videos)",
        )
        frames = await asyncio.to_thread(
            VideoService.extract_frames_as_jpeg_bytes,
            video.data,
            video.duration_seconds,
            15,
            85,
        )

        self.logger.info(
            "Frames generated: " + str(len(frames)),
        )
        self.logger.info(
            "Zipping frames...",
        )
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for name, jpeg_bytes in frames:
                zipf.writestr(name, jpeg_bytes)

        self.logger.info(
            "Uploading zip to blob storage...",
        )
        zip_path = f"{video.user_id}/thumbnails/{video.video_id}.zip"
        await self.__blob_storage.upload_file(zip_path, zip_buffer.getvalue())
        self.logger.info(
            "Zip uploaded to blob storage",
        )
        video.set_thumbnails_path(zip_path)
        return video