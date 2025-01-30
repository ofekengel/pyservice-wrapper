import sys
from typing import Callable, Generator, Type, TypeVar, overload

from service_wrapper.utils.utils import ServiceData, ServiceFunction, serve_forever
from service_wrapper.windows.base_service import BaseService
from service_wrapper.windows.service_utils import DefaultService, entrypoint

_B = TypeVar("_B", bound=BaseService)
_T = TypeVar("_T")


def as_service(
    name: str,
    display_name: str,
    service_entrypoint: str = "",
    svc_class: Type[_B] = DefaultService,
) -> Callable[[Callable[[], Generator]], ServiceFunction[ServiceData[Type[_B]]]]:
    def inner(function: Callable[[], Generator]):
        data = ServiceData(name, display_name, service_entrypoint, function, svc_class)
        if len(sys.argv) > 1 and sys.argv[1] == service_entrypoint:
            func = entrypoint(data)
        else:
            # will run cleanup on Exception (KeyboardInterrupt)
            func = serve_forever(function)

        func.__service__ = data
        return func

    return inner
