from typing import Optional


class DomainException(Exception):
    def __init__(self, code: str, message: Optional[str] = None):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message if message else ""}")
