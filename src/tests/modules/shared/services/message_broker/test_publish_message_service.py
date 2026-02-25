import pytest
from faker import Faker
from pytest_mock import MockFixture

from modules.shared.services.message_broker.publish_message_service import (
    PublishMessageService,
)


@pytest.mark.asyncio
class TestPublishMessageService:
    @pytest.fixture
    def publish_message_service(self, mocker: MockFixture) -> PublishMessageService:
        self.faker = Faker()
        self.rabbitmq_publisher = mocker.MagicMock()
        self.rabbitmq_publisher.publish = mocker.AsyncMock()
        return PublishMessageService(rabbitmq_publisher=self.rabbitmq_publisher)

    @pytest.mark.asyncio
    async def test_publish(self, publish_message_service: PublishMessageService):
        queue_name = "test_queue"
        message = {"test": "data"}

        await publish_message_service.publish(queue_name=queue_name, message=message)

        self.rabbitmq_publisher.publish.assert_called_once_with(queue_name, message)
