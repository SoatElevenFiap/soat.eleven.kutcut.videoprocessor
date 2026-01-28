from abc import ABC
from typing import Optional

from modules.shared.services.logger.logger_service import LoggerService


class InfraService(ABC):
    def __init__(self, context: Optional[str] = "Logger"):
        self.logger = LoggerService(context)
