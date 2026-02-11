from typing import Optional

from modules.shared.constants.exceptions_constants import ExceptionConstants
from modules.shared.exceptions.domain_exception import DomainException


class VideoNotFoundException(DomainException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(ExceptionConstants.VIDEO_NOT_FOUND, message)
