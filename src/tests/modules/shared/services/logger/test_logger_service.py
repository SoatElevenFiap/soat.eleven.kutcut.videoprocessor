import pytest
from unittest.mock import patch, MagicMock

from modules.shared.services.logger.logger_service import LoggerService


@pytest.fixture
def mock_logger():
    with patch("modules.shared.services.logger.logger_service.logger") as mock:
        yield mock


def test_logger_initialization(mock_logger):
    # Setting up the logger tests
    mock_logger.bind.return_value.opt.return_value = MagicMock()
    
    LoggerService("test_context")
    mock_logger.remove.assert_called_once()
    assert mock_logger.level.call_count == 4
    mock_logger.add.assert_called_once()
    mock_logger.bind.assert_called_with(context="test_context")


def test_logger_methods():
    with patch("modules.shared.services.logger.logger_service.logger") as mock_base_logger:
        mock_bound_logger = MagicMock()
        mock_base_logger.bind.return_value.opt.return_value = mock_bound_logger
        mock_bound_logger.bind.return_value = mock_bound_logger # for inner chained .bind() calls

        logger_service = LoggerService("test_context")
        
        logger_service.debug("debug message")
        mock_bound_logger.debug.assert_called_with("debug message")

        logger_service.info("info message")
        mock_bound_logger.info.assert_called_with("info message")

        logger_service.warning("warning message")
        mock_bound_logger.warning.assert_called_with("warning message")

        logger_service.error("error message")
        mock_bound_logger.error.assert_called_with("error message")


def test_logger_formatting_methods():
    with patch("modules.shared.services.logger.logger_service.logger") as mock_base_logger:
        mock_bound_logger = MagicMock()
        mock_base_logger.bind.return_value.opt.return_value = mock_bound_logger
        mock_bound_logger.bind.return_value = mock_bound_logger

        logger_service = LoggerService("test_context")
        
        # Test title_box
        logger_service.title_box("TEST")
        assert mock_bound_logger.info.call_count == 3
        
        # Test title_box_warning
        logger_service.title_box_warning("WARN")
        assert mock_bound_logger.warning.call_count == 3
        
        # Test title_box_error
        logger_service.title_box_error("ERR")
        assert mock_bound_logger.error.call_count == 3
        
        # Test dict_to_table
        logger_service.dict_to_table({"key": "value"})
        assert mock_bound_logger.info.call_count >= 3 # title, box lines, footer
