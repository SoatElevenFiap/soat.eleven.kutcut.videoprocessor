import asyncio
import sys

from aio_pika import connect_robust

from containers import containers
from modules.shared.services.settings.settings import Settings
from modules.video.controllers.video_controller import VideoController


async def run_worker() -> None:
    settings = Settings()
    connection = await connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(
        settings.rabbitmq_queue_video_process, durable=True
    )
    video_controller = VideoController(containers.video_process_application_service)
    print(f"Worker started. Waiting for messages on queue: {settings.rabbitmq_queue_video_process}")
    await queue.consume(video_controller.consume)
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        await connection.close()
        raise


def main() -> None:
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
