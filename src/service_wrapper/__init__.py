import sys
from typing import Callable, Generator, overload, TypeVar, Type
from typing_extensions import TypeIs

from service_wrapper.base_service import BaseService
from service_wrapper.service_wrapper import ServiceFunction, DefaultService, entrypoint
from service_wrapper.service_wrapper_utils import serve_forever

_B = TypeVar("_B", bound=BaseService)
_T = TypeVar("_T")

SERVICE_MAGIC = "__service__"


@overload
def as_service(
        name: str,
        display_name: str,
        service_entrypoint: str = "",
) -> Callable[[Callable[[], Generator]], ServiceFunction[Type[DefaultService]]]: ...


@overload
def as_service(
        name: str,
        display_name: str,
        service_entrypoint: str = "",
        base: Type[_B] = DefaultService,
) -> Callable[[Callable[[], Generator]], ServiceFunction[Type[_B]]]: ...


def as_service(
        name: str,
        display_name: str,
        service_entrypoint: str = "",
        base: Type[_B] = DefaultService,
) -> Callable[[Callable[[], Generator]], ServiceFunction[Type[_B]]]:
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

    class WindowsService(base):
        _svc_name_ = name
        _svc_display_name_ = display_name
        _svc_entrypoint_ = service_entrypoint

    def inner(function: Callable[[], Generator]):
        generator = function()
        WindowsService.LOGIC = generator

        if len(sys.argv) > 1 and sys.argv[1] == service_entrypoint:
            func = entrypoint(WindowsService)
        else:
            # will run cleanup on Exception (KeyboardInterrupt)
            func = serve_forever(generator)

        func.__service__ = WindowsService
        return func

    return inner


def is_service(function: Callable) -> TypeIs[ServiceFunction[_T]]:
    return hasattr(function, SERVICE_MAGIC)


def get_service(function: ServiceFunction[_T]) -> _T:
    if is_service(function):
        return getattr(function, SERVICE_MAGIC)
    raise ValueError("function is not a service")

__all__ = [
    "as_service",
    "is_service",
    "get_service",
]
