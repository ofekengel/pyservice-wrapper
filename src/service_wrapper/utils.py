import asyncio
import contextlib
import inspect
from typing import Callable, Generator


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
