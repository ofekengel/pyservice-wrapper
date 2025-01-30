from typing import TYPE_CHECKING, Callable, Generator, Type, TypeVar, overload

from service_wrapper.utils.service_tools import IServiceTools
from service_wrapper.utils.utils import ServiceData, ServiceFunction, get_service

try:
    from service_wrapper.windows.service_tools import ServiceTools
    from service_wrapper.windows.windows_wrapper import as_service as as_service_
except ImportError:
    from service_wrapper.linux.linux_tools import ServiceTools
    from service_wrapper.linux.linux_wrapper import as_service as as_service_


if TYPE_CHECKING:
    from service_wrapper.windows.base_service import BaseService
    from service_wrapper.windows.service_utils import DefaultService

    _B = TypeVar("_B", bound=BaseService)

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
    ) -> Callable[
        [Callable[[], Generator]], ServiceFunction[ServiceData[Type[_B]]]
    ]: ...

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
        """

else:
    as_service = as_service_


def get_service_tools(service_function: ServiceFunction) -> IServiceTools:
    return ServiceTools(get_service(service_function))
