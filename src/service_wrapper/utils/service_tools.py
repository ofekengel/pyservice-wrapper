from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

_T = TypeVar("_T")


class IServiceTools(ABC, Generic[_T]):
    service: _T

    @abstractmethod
    def start_service(self):
        raise NotImplemented()

    @abstractmethod
    def stop_service(self):
        raise NotImplemented()

    @abstractmethod
    def install_service(self, binary_path: Path):
        raise NotImplemented()

    @abstractmethod
    def uninstall_service(self):
        raise NotImplemented()
