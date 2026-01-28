from abc import ABC, abstractmethod
from typing import Optional


class CacheAdapter(ABC):
    @abstractmethod
    def get_value(self, key: str, default_value: Optional[str] = None) -> Optional[str]:
        raise NotImplementedError("Method get_value must be implemented")

    @abstractmethod
    def set_value(
        self, key: str, value: str, expire_in_milliseconds: Optional[int] = None
    ) -> bool:
        raise NotImplementedError("Method set_value must be implemented")

    @abstractmethod
    def delete_value(self, key: str) -> bool:
        raise NotImplementedError("Method delete_value must be implemented")
