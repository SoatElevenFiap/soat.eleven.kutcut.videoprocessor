import pytest
from faker import Faker
from pytest_mock import MockFixture

from modules.video.entities.video_entity import VideoEntity
from modules.video.exceptions import VideoNotFoundException
from modules.video.services.application.get_video_process_application_service import (
    GetVideoProcessApplicationService,
)


@pytest.mark.asyncio
class TestGetVideoProcessApplicationService:
    @pytest.fixture
    def application_service(
        self, mocker: MockFixture
    ) -> GetVideoProcessApplicationService:
        self.faker = Faker()
        self.download_service = mocker.MagicMock()
        self.download_service.process = mocker.AsyncMock()

        self.generate_service = mocker.MagicMock()
        self.generate_service.process = mocker.AsyncMock()

        self.publish_service = mocker.MagicMock()
        self.publish_service.publish = mocker.AsyncMock()

        self.settings = mocker.MagicMock()
        self.settings.rabbitmq_queue_video_process_completed = "test_queue"

        return GetVideoProcessApplicationService(
            download_video_domain_service=self.download_service,
            generate_snapshots_domain_service=self.generate_service,
            publish_message_service=self.publish_service,
            settings=self.settings,
        )

    @pytest.fixture
    def video_entity(self) -> VideoEntity:
        entity = VideoEntity(
            user_id=self.faker.uuid4(),
            video_id=self.faker.file_name(category="video"),
            data=b"data",
            size_bytes=4,
            duration_seconds=10,
        )
        entity.set_thumbnails_path(f"{entity.user_id}/thumbnails/{entity.video_id}.zip")
        return entity

    @pytest.mark.asyncio
    async def test_process_success(
        self,
        application_service: GetVideoProcessApplicationService,
        video_entity: VideoEntity,
    ):
        user_id = video_entity.user_id
        filename = video_entity.video_id
        title = self.faker.sentence()
        message_id = self.faker.uuid4()

        self.download_service.process.return_value = video_entity
        self.generate_service.process.return_value = video_entity

        result = await application_service.process(
            user_id=user_id, filename=filename, title=title, message_id=message_id
        )

        expected_payload = {
            "userId": user_id,
            "filename": filename,
            "title": title,
            "messageId": message_id,
            "thumbnailsPath": video_entity.thumbnails_path,
            "status": 4,
            "result": "success",
            "code": "S200",
        }

        assert result == expected_payload
        self.publish_service.publish.assert_called_once_with(
            "test_queue", expected_payload
        )

    @pytest.mark.asyncio
    async def test_process_video_not_found(
        self, application_service: GetVideoProcessApplicationService
    ):
        user_id = self.faker.uuid4()
        filename = self.faker.file_name(category="video")
        title = self.faker.sentence()
        message_id = self.faker.uuid4()

        self.download_service.process.side_effect = VideoNotFoundException("not found")

        result = await application_service.process(
            user_id=user_id, filename=filename, title=title, message_id=message_id
        )

        expected_payload = {
            "userId": user_id,
            "filename": filename,
            "title": title,
            "messageId": message_id,
            "status": 5,
            "result": "error",
            "code": "E404",
        }

        assert result == expected_payload
        self.publish_service.publish.assert_called_once_with(
            "test_queue", expected_payload
        )
        self.generate_service.process.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_unexpected_error(
        self, application_service: GetVideoProcessApplicationService
    ):
        user_id = self.faker.uuid4()
        filename = self.faker.file_name(category="video")
        title = self.faker.sentence()
        message_id = self.faker.uuid4()

        self.download_service.process.side_effect = Exception("unexpected error")

        with pytest.raises(Exception, match="unexpected error"):
            await application_service.process(
                user_id=user_id, filename=filename, title=title, message_id=message_id
            )

        expected_payload = {
            "userId": user_id,
            "filename": filename,
            "title": title,
            "messageId": message_id,
            "status": 5,
            "result": "error",
            "code": "E500",
        }
        self.publish_service.publish.assert_called_once_with(
            "test_queue", expected_payload
        )
