import sys
from typing import Callable, Generator, Type, TypeVar, overload

from typing_extensions import TypeIs

from service_wrapper.base_service import BaseService
from service_wrapper.ext import BlockingService
from service_wrapper.service_wrapper import (
    DefaultService,
    ServiceFunction,
    entrypoint,
    ServiceData,
)
from service_wrapper.utils import serve_forever

_B = TypeVar("_B", bound=BaseService)
_T = TypeVar("_T")

SERVICE_MAGIC = "__service__"


@overload
def as_service(
    name: str,
    display_name: str,
    service_entrypoint: str = "",
) -> Callable[
    [Callable[[], Generator]], ServiceFunction[ServiceData[Type[DefaultService]]]
]: ...


@overload
def as_service(
    name: str,
    display_name: str,
    service_entrypoint: str = "",
    svc_class: Type[_B] = DefaultService,
) -> Callable[[Callable[[], Generator]], ServiceFunction[ServiceData[Type[_B]]]]: ...


def as_service(
    name: str,
    display_name: str,
    service_entrypoint: str = "",
    svc_class: Type[_B] = DefaultService,
) -> Callable[[Callable[[], Generator]], ServiceFunction[ServiceData[Type[_B]]]]:
    """
    .. code-block:: python

        @as_service(SERVICE_NAME, SERVICE_DISPLAY_NAME, SERVICE_ENTRYPOINT_COMMAND)
        def main():
            # startup
            try:
                yield
            finally:
                # cleanup
            if __name__ == "__main__":
            main()


    `startup` should be None blocking.
    lifecycle of your service will be controlled externally
    (yield in `main` gives control to function)
    `cleanup` should exit in a timely fashion.

    code runs normally from terminal (ie `python service_main.py`).
    when running from terminal, `main` will run forever - until `KeyboardInterrupt`

    you can optionally opt for implementing your own service class to get more control
    """

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


def is_service(function: Callable) -> TypeIs[ServiceFunction[_T]]:
    return hasattr(function, SERVICE_MAGIC)


def get_service(
    function: ServiceFunction[ServiceData[Type[_B]]],
) -> ServiceData[Type[_B]]:
    if is_service(function):
        return getattr(function, SERVICE_MAGIC)
    raise ValueError("function is not a service")


__all__ = [
    "as_service",
    "is_service",
    "get_service",
]
