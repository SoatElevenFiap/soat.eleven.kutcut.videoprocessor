import pytest
from faker import Faker
from pytest_mock import MockFixture

from modules.video.services.domain.download_video_domain_service import (
    DownloadVideoDomainService,
)


@pytest.mark.asyncio
class TestDownloadVideoDomainService:
    @pytest.fixture
    def download_video_domain_service(
        self, mocker: MockFixture
    ) -> DownloadVideoDomainService:
        self.faker = Faker()
        self.blob_storage = mocker.MagicMock()
        self.blob_storage.exists = mocker.AsyncMock()
        self.blob_storage.download_file = mocker.AsyncMock()
        return DownloadVideoDomainService(blob_storage=self.blob_storage)

    @pytest.mark.asyncio
    async def test_process_success(
        self,
        download_video_domain_service: DownloadVideoDomainService,
        mocker: MockFixture,
    ):
        user_id = self.faker.uuid4()
        filename = self.faker.file_name(category="video")
        video_data = b"fake_video_bytes"

        self.blob_storage.exists.return_value = True
        self.blob_storage.download_file.return_value = video_data

        mocker.patch(
            "modules.video.services.domain.download_video_domain_service.VideoService.get_video_duration_seconds",
            return_value=120,
        )

        result = await download_video_domain_service.process(
            user_id=user_id, filename=filename
        )

        assert result is not None
        assert result.user_id == user_id
        assert result.video_id == filename
        assert result.data == video_data
        assert result.duration_seconds == 120
        self.blob_storage.exists.assert_called_once_with(f"{user_id}/videos/{filename}")
        self.blob_storage.download_file.assert_called_once_with(
            f"{user_id}/videos/{filename}"
        )

    @pytest.mark.asyncio
    async def test_process_video_not_found(
        self, download_video_domain_service: DownloadVideoDomainService
    ):
        user_id = self.faker.uuid4()
        filename = self.faker.file_name(category="video")

        self.blob_storage.exists.return_value = False

        from modules.video.exceptions import VideoNotFoundException

        with pytest.raises(VideoNotFoundException) as exc_info:
            await download_video_domain_service.process(
                user_id=user_id, filename=filename
            )

        assert f"Video not found for user id {user_id} and filename {filename}" in str(
            exc_info.value
        )
        self.blob_storage.download_file.assert_not_called()
