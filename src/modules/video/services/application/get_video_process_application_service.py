from modules.shared.adapters import ApplicationService
from modules.video.services.domain.download_video_domain_service import (
    DownloadVideoDomainService,
)
from modules.video.services.domain.generate_snapshots_domain_service import (
    GenerateSnapshotsDomainService,
)


class GetVideoProcessApplicationService(ApplicationService):
    def __init__(
        self,
        download_video_domain_service: DownloadVideoDomainService,
        generate_snapshots_domain_service: GenerateSnapshotsDomainService,
    ) -> None:
        super().__init__(GetVideoProcessApplicationService.__name__)
        self.__download_video_domain_service = download_video_domain_service
        self.__generate_snapshots_domain_service = generate_snapshots_domain_service

    async def process(self, user_id: str, video_id: str) -> dict:
        self.logger.info(
            "Getting video process for user id "
            + user_id
            + " and video id "
            + video_id,
        )

        video = await self.__download_video_domain_service.process(
            user_id=user_id,
            video_id=video_id,
        )
        generated_video = await self.__generate_snapshots_domain_service.process(video)
        self.logger.info(
            "Video process completed for user id " + user_id + " and video id " + video_id,
        )
        return {
            "user_id": user_id,
            "video_id": video_id,
            "thumbnails_path": generated_video.thumbnails_path,
        }
