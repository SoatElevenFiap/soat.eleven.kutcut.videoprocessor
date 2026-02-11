from abc import ABC, abstractmethod


class BlobStorageAdapter(ABC):
    @abstractmethod
    async def download_file(
        self,
        path: str,
    ) -> bytes:
        """
        Busca o conteúdo de um arquivo como bytes.

        Args:
            path: Caminho do arquivo (ex.: exemplo/videos/arquivo.mkv).

        Returns:
            Conteúdo do arquivo em bytes.

        Raises:
            FileNotFoundError ou equivalente se o arquivo não existir.
        """
        raise NotImplementedError("Method download_file must be implemented")

    @abstractmethod
    async def exists(
        self,
        path: str,
    ) -> bool:
        """Verifica se o arquivo existe no blob."""
        raise NotImplementedError("Method exists must be implemented")

    @abstractmethod
    async def upload_file(
        self,
        path: str,
        data: bytes,
    ) -> None:
        """Faz upload do conteúdo para um arquivo."""
        raise NotImplementedError("Method upload_file must be implemented")
