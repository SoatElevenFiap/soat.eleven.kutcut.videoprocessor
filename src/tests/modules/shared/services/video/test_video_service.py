import pytest
from unittest.mock import patch, MagicMock

import av
from modules.shared.services.video.video_service import VideoService


def test_video_service_duration_no_container():
    # If the container fails to parse it raises exception usually, but passing an empty 
    # mock byte object to show that it returns 0 if no duration is found in stream or container
    with patch("modules.shared.services.video.video_service.av.open") as mock_open:
        mock_container = MagicMock()
        mock_stream = MagicMock()
        mock_stream.duration = None
        mock_container.streams.video = [mock_stream]
        mock_container.duration = None
        mock_open.return_value.__enter__.return_value = mock_container

        duration = VideoService.get_video_duration_seconds(b"data")
        assert duration == 0


def test_video_service_duration_from_stream():
    with patch("modules.shared.services.video.video_service.av.open") as mock_open:
        mock_container = MagicMock()
        mock_stream = MagicMock()
        mock_stream.duration = 5000
        mock_stream.time_base = 0.01  # 5000 * 0.01 = 50 seconds
        mock_container.streams.video = [mock_stream]
        mock_open.return_value.__enter__.return_value = mock_container

        duration = VideoService.get_video_duration_seconds(b"data")
        assert duration == 50


def test_video_service_duration_from_container():
    with patch("modules.shared.services.video.video_service.av.open") as mock_open:
        mock_container = MagicMock()
        mock_stream = MagicMock()
        mock_stream.duration = None
        mock_container.streams.video = [mock_stream]
        
        # Assume av.time_base is 1000000 for standard ffmpeg mock
        with patch("modules.shared.services.video.video_service.av.time_base", 0.000001):
            mock_container.duration = 60000000  # 60 seconds
            mock_open.return_value.__enter__.return_value = mock_container
    
            duration = VideoService.get_video_duration_seconds(b"data")
            assert duration == 60


@patch("modules.shared.services.video.video_service.av.open")
def test_extract_frames_as_jpeg_bytes_empty_targets(mock_open):
    result = VideoService.extract_frames_as_jpeg_bytes(b"data", duration_seconds=0, interval_seconds=15)
    assert result == []


def test_extract_frames_as_jpeg_bytes_with_mock():
    with patch("modules.shared.services.video.video_service.av.open") as mock_open:
        mock_container = MagicMock()
        mock_stream = MagicMock()
        mock_container.streams.video = [mock_stream]
        
        # Create a mock frame that happens at 15 seconds
        mock_frame = MagicMock()
        mock_frame.time = 15.0
        mock_image = MagicMock()
        mock_frame.to_image.return_value = mock_image
        
        mock_container.decode.return_value = [mock_frame]
        mock_open.return_value.__enter__.return_value = mock_container

        # We request frames for a 16s video at interval 15s (targets: 0, 15)
        # However, the loop continues skipping until it finds an exact/greater time stamp.
        result = VideoService.extract_frames_as_jpeg_bytes(b"data", duration_seconds=16, interval_seconds=15)
        
        # It should extract the 15s target using our single frame mock.
        # Since our mock only provides 15.0, the target at 0s might be skipped if no frame <= 0.
        # Wait, the code logic: if t_sec < targets[next_i]: continue
        # Since `t_sec = 15.0` and `targets[0] = 0.0`, it will start processing immediately.
        # Then `targets[1] = 15.0`. It should process both targets with the same frame if it satisfies the while loop condition.
        assert len(result) == 2
        assert result[0][0] == "snapshot_0000s.jpg"
        assert result[1][0] == "snapshot_0015s.jpg"
        mock_image.save.assert_called()
