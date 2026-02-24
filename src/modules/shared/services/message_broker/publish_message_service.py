from modules.shared.adapters.message_broker.rabbitmq_publisher import RabbitMQPublisher


class PublishMessageService:
    def __init__(self, rabbitmq_publisher: RabbitMQPublisher):
        self.__rabbitmq_publisher = rabbitmq_publisher

    async def publish(self, queue_name: str, message: dict) -> None:
        await self.__rabbitmq_publisher.publish(queue_name, message)
