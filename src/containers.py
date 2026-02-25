from modules.shared.adapters.message_broker.rabbitmq_publisher import RabbitMQPublisher
from modules.shared.services.azure import AzureBlobStorageService
from modules.shared.services.message_broker.publish_message_service import (
    PublishMessageService,
)
from modules.shared.services.settings.settings import Settings
from modules.video.services.application.get_video_process_application_service import (
    GetVideoProcessApplicationService,
)
from modules.video.services.domain import (
    DownloadVideoDomainService,
    GenerateSnapshotsDomainService,
)


class Containers:
    _instance: "Containers | None" = None

    def __new__(cls) -> "Containers":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        settings = Settings()
        self._settings = settings
        self._blob_storage = (
            AzureBlobStorageService(
                settings.blob_storage_connection_string,
                container_name=settings.blob_storage_container_name,
            )
            if settings.blob_storage_connection_string
            else None
        )
        download_video_domain_service = DownloadVideoDomainService(self._blob_storage)
        generate_snapshots_domain_service = GenerateSnapshotsDomainService(
            self._blob_storage
        )
        self.rabbitmq_publisher = RabbitMQPublisher(settings.rabbitmq_url)
        self.publish_message_service = PublishMessageService(self.rabbitmq_publisher)

        self.video_process_application_service = GetVideoProcessApplicationService(
            download_video_domain_service=download_video_domain_service,
            generate_snapshots_domain_service=generate_snapshots_domain_service,
            publish_message_service=self.publish_message_service,
            settings=settings,
        )
        self._initialized = True


containers = Containers()
