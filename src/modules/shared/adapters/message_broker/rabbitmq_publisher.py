import json

from aio_pika import Message, connect_robust


class RabbitMQPublisher:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url

    async def publish(self, queue_name: str, message: dict) -> None:
        connection = await connect_robust(self.rabbitmq_url)
        try:
            async with connection:
                channel = await connection.channel()
                await channel.declare_queue(queue_name, durable=True)

                body = json.dumps(message).encode()
                msg = Message(body=body)

                await channel.default_exchange.publish(
                    msg,
                    routing_key=queue_name,
                )
        finally:
            if not connection.is_closed:
                await connection.close()
