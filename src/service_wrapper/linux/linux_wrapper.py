import warnings
from dataclasses import dataclass
from typing import Callable, Generator, Generic, Type, TypeVar

from service_wrapper.utils.utils import ServiceFunction, serve_forever

_T = TypeVar("_T")


# todo: merge with the other one?
@dataclass
class ServiceData(Generic[_T]):
    name: str
    display_name: str
    entrypoint: str
    logic: Callable
    svc_class: _T


def as_service(
    name: str,
    display_name: str,
    service_entrypoint: str = "",
    svc_class: Type[object] = None,
) -> Callable[[Callable[[], Generator]], ServiceFunction[ServiceData[Type[_T]]]]:
    if svc_class is not None:
        warnings.warn("linux does not support svc_class, ignoring")

    def inner(function: Callable[[], Generator]):
        # will run cleanup on Exception (KeyboardInterrupt)
        func = serve_forever(function)
        func.__service__ = ServiceData(
            name, display_name, service_entrypoint, function, svc_class
        )
        return func

    return inner
