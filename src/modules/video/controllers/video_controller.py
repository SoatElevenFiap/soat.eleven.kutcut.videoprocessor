import json

from aio_pika.abc import AbstractIncomingMessage

from modules.shared.adapters.message_broker.message_broker_adapter import (
    MessageBrokerAdapter,
)
from modules.video.models.video_message_model import VideoMessageModel
from modules.video.services.application.get_video_process_application_service import (
    GetVideoProcessApplicationService,
)


class VideoController(MessageBrokerAdapter):
    def __init__(
        self, video_process_application_service: GetVideoProcessApplicationService
    ):
        super().__init__(queue_name="video.process")
        self.__video_process_application_service = video_process_application_service

    async def consume(self, message: AbstractIncomingMessage):
        async with message.process(ignore_processed=True):
            received_message = json.loads(message.body.decode())
            video_message = VideoMessageModel(**received_message)
            await self.__video_process_application_service.process(
                user_id=video_message.user_id,
                video_id=video_message.video_id,
            )
