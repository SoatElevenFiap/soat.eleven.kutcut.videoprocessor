from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: Optional[str] = None
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_queue_video_process: str = "video_uploaded"
    rabbitmq_queue_video_process_completed: str = "processamento_de_videos"
    rabbitmq_prefetch_count: int = 10
    blob_storage_connection_string: str = ""
    blob_storage_container_name: str = "videos"

    @field_validator("blob_storage_connection_string")
    @classmethod
    def validate_blob_connection_string(cls, v: str) -> str:
        if not v:
            return v
        if "AccountName=" not in v:
            raise ValueError(
                "blob_storage_connection_string parece truncada (falta AccountName=). "
                'No .env use aspas duplas: BLOB_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"'
            )
        return v

    def is_development(self) -> bool:
        return self.environment == "development"

    class Config:
        env_file = ".env"
        extra = "ignore"
