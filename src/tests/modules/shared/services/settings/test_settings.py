import os
import pytest
from pydantic import ValidationError
from unittest.mock import patch

from modules.shared.services.settings.settings import Settings


def test_settings_initialization_defaults():
    # If no env vars are set, it should use defaults, but since pydantic might read existing .env
    # we enforce a clean environment for this test.
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings(_env_file=None, blob_storage_connection_string="")
        assert settings.rabbitmq_queue_video_process == "video_uploaded"
        assert settings.rabbitmq_queue_video_process_completed == "processamento_de_videos"
        assert settings.rabbitmq_prefetch_count == 10
        assert settings.is_development() is False


def test_settings_blob_validator_valid():
    valid_conn = "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=key;EndpointSuffix=core.windows.net"
    settings = Settings(blob_storage_connection_string=valid_conn)
    assert settings.blob_storage_connection_string == valid_conn


def test_settings_blob_validator_invalid():
    invalid_conn = "DefaultEndpointsProtocol=https;AccountKey=key" # missing AccountName=
    with pytest.raises(ValidationError) as exc_info:
        Settings(blob_storage_connection_string=invalid_conn)
    
    assert "blob_storage_connection_string parece truncada" in str(exc_info.value)


def test_settings_is_development():
    settings = Settings(environment="development", blob_storage_connection_string="")
    assert settings.is_development() is True
    
    settings = Settings(environment="production", blob_storage_connection_string="")
    assert settings.is_development() is False
