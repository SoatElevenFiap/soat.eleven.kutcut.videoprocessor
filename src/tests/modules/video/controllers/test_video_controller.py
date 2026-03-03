import json

import pytest
from faker import Faker
from pytest_mock import MockFixture

from modules.video.controllers.video_controller import VideoController


@pytest.mark.asyncio
class TestVideoController:
    @pytest.fixture
    def application_service(self, mocker: MockFixture):
        service = mocker.MagicMock()
        service.process = mocker.AsyncMock()
        return service

    @pytest.fixture
    def video_controller(self, application_service) -> VideoController:
        self.faker = Faker()
        return VideoController(video_process_application_service=application_service)

    @pytest.mark.asyncio
    async def test_consume_success(
        self,
        video_controller: VideoController,
        application_service,
        mocker: MockFixture,
    ):
        message = mocker.MagicMock()
        process_context = mocker.AsyncMock()
        message.process.return_value = process_context

        user_id = self.faker.uuid4()
        filename = self.faker.file_name(category="video")
        title = self.faker.sentence()
        message_id = self.faker.uuid4()

        payload = {
            "userId": user_id,
            "filename": filename,
            "title": title,
            "messageId": message_id,
        }
        message.body = json.dumps(payload).encode()

        await video_controller.consume(message)

        message.process.assert_called_once_with(ignore_processed=True)
        application_service.process.assert_called_once_with(
            user_id=user_id,
            filename=filename,
            title=title,
            message_id=message_id,
        )
