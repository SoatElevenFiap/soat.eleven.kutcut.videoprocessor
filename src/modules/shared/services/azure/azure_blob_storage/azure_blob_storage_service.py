from typing import Optional

from azure.storage.blob.aio import BlobServiceClient

from modules.shared.adapters.blob_storage.blob_storage_adapter import BlobStorageAdapter


class AzureBlobStorageService(BlobStorageAdapter):
    def __init__(self, connection_string: str, container_name: Optional[str] = None):
        super().__init__()
        self.__connection_string = connection_string
        self.__client = BlobServiceClient.from_connection_string(
            self.__connection_string
        )
        self.__container_name = container_name if container_name else ""

    async def download_file(self, path: str) -> bytes:
        blob_client = self.__client.get_blob_client(self.__container_name, path)
        stream = await blob_client.download_blob()
        return await stream.readall()

    async def upload_file(self, path: str, data: bytes) -> None:
        blob_client = self.__client.get_blob_client(self.__container_name, path)
        await blob_client.upload_blob(data)

    async def exists(self, path: str) -> bool:
        blob_client = self.__client.get_blob_client(self.__container_name, path)
        return await blob_client.exists()
