import io
import zipfile

import pytest
from faker import Faker
from pytest_mock import MockFixture

from modules.video.entities.video_entity import VideoEntity
from modules.video.services.domain.generate_snapshots_domain_service import (
    GenerateSnapshotsDomainService,
)


@pytest.mark.asyncio
class TestGenerateSnapshotsDomainService:
    @pytest.fixture
    def generate_snapshots_domain_service(
        self, mocker: MockFixture
    ) -> GenerateSnapshotsDomainService:
        self.faker = Faker()
        self.blob_storage = mocker.MagicMock()
        self.blob_storage.upload_file = mocker.AsyncMock()
        return GenerateSnapshotsDomainService(blob_storage=self.blob_storage)

    @pytest.fixture
    def video_entity(self) -> VideoEntity:
        return VideoEntity(
            user_id=self.faker.uuid4(),
            video_id=self.faker.file_name(category="video"),
            data=b"fake_video_data",
            size_bytes=1024,
            duration_seconds=60,
        )

    @pytest.mark.asyncio
    async def test_process_success(
        self,
        generate_snapshots_domain_service: GenerateSnapshotsDomainService,
        video_entity: VideoEntity,
        mocker: MockFixture,
    ):
        fake_frames = [
            ("snapshot_0000s.jpg", b"jpeg_data_1"),
            ("snapshot_0015s.jpg", b"jpeg_data_2"),
        ]

        mocker.patch(
            "modules.video.services.domain.generate_snapshots_domain_service.VideoService.extract_frames_as_jpeg_bytes",
            return_value=fake_frames,
        )

        result_video = await generate_snapshots_domain_service.process(
            video=video_entity
        )

        assert result_video is video_entity
        import os
        video_name = os.path.splitext(video_entity.video_id)[0]
        expected_zip_path = (
            f"{video_entity.user_id}/thumbnails/{video_name}.zip"
        )
        assert result_video.thumbnails_path == expected_zip_path

        self.blob_storage.upload_file.assert_called_once()
        call_args = self.blob_storage.upload_file.call_args[0]
        assert call_args[0] == expected_zip_path

        # Verify the zip contents
        zip_bytes = call_args[1]
        zip_buffer = io.BytesIO(zip_bytes)
        with zipfile.ZipFile(zip_buffer, "r") as zipf:
            assert zipf.namelist() == ["snapshot_0000s.jpg", "snapshot_0015s.jpg"]
            assert zipf.read("snapshot_0000s.jpg") == b"jpeg_data_1"
            assert zipf.read("snapshot_0015s.jpg") == b"jpeg_data_2"
