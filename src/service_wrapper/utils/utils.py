import asyncio
import contextlib
import inspect
from dataclasses import dataclass
from typing import Callable, Generator, Generic, Protocol, TypeVar

from typing_extensions import TypeIs

_T = TypeVar("_T")
_B = TypeVar("_B")


class ServiceFunction(Protocol[_T]):
    __service__: _T

    def __call__(self) -> ...: ...


def wait_forever():
    async def wait():
        await asyncio.Event().wait()

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.run_until_complete(wait())
    else:
        asyncio.run(wait())


def serve_forever(func: Callable):
    if inspect.isgeneratorfunction(func) is False:
        return func

    generator: Generator = func()

    def wrapper():
        generator.send(None)
        try:
            wait_forever()  # will raise KeyboardInterrupt
        except KeyboardInterrupt:
            raise KeyboardInterrupt() from None
        finally:
            with contextlib.suppress(StopIteration):
                generator.send(None)

    return wrapper


SERVICE_MAGIC = "__service__"


def is_service(function: Callable) -> TypeIs[ServiceFunction[_T]]:
    return hasattr(function, SERVICE_MAGIC)


def get_service(
    function: ServiceFunction[_T],
):
    if is_service(function):
        return function.__service__
    raise ValueError("function is not a service")


@dataclass
class ServiceData(Generic[_B]):
    name: str
    display_name: str
    entrypoint: str
    logic: Callable
    svc_class: _B
