from modules.shared.adapters import ApplicationService
from modules.shared.services.message_broker.publish_message_service import (
    PublishMessageService,
)
from modules.shared.services.settings.settings import Settings
from modules.video.exceptions import VideoNotFoundException
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
        publish_message_service: PublishMessageService,
        settings: Settings,
    ) -> None:
        super().__init__(GetVideoProcessApplicationService.__name__)
        self.__download_video_domain_service = download_video_domain_service
        self.__generate_snapshots_domain_service = generate_snapshots_domain_service
        self.__publish_message_service = publish_message_service
        self.__settings = settings

    async def process(self, user_id: str, filename: str, title: str, message_id: str) -> dict:
        self.logger.info(
            f"Getting video process for user id {user_id} and filename {filename}",
        )
        queue_name = self.__settings.rabbitmq_queue_video_process_completed

        try:
            video = await self.__download_video_domain_service.process(
                user_id=user_id,
                filename=filename,
            )
            generated_video = await self.__generate_snapshots_domain_service.process(
                video
            )

            payload = {
                "userId": user_id,
                "filename": filename,
                "title": title,
                "messageId": message_id,
                "thumbnailsPath": generated_video.thumbnails_path,
                "status": 4,
                "result": "success",
                "code": "S200",
            }
            await self.__publish_message_service.publish(queue_name, payload)

            self.logger.info(
                f"Video process completed for user id {user_id} and filename {filename}",
            )
            return payload

        except VideoNotFoundException:
            self.logger.error(
                f"Video not found for user id {user_id} and filename {filename}",
            )
            payload = {
                "userId": user_id,
                "filename": filename,
                "title": title,
                "messageId": message_id,
                "status": 5,
                "result": "error",
                "code": "E404",
            }
            await self.__publish_message_service.publish(queue_name, payload)
            return payload
        except Exception as e:
            self.logger.error(
                f"Error processing video for user id {user_id} and filename {filename}: {e}",
            )
            payload = {
                "userId": user_id,
                "filename": filename,
                "title": title,
                "messageId": message_id,
                "status": 5,
                "result": "error",
                "code": "E500",
            }
            await self.__publish_message_service.publish(queue_name, payload)
            raise e
