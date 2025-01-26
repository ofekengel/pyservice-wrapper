import contextlib
import logging
from dataclasses import dataclass
from typing import Protocol, TypeVar, Callable, Generic, Type, ContextManager

import servicemanager
import win32event
import win32service

from service_wrapper.base_service import BaseService

_T = TypeVar("_T")
_B = TypeVar("_B", bound=Type[BaseService])


class ServiceFunction(Protocol[_T]):
    __service__: _T

    def __call__(self) -> ...: ...


class DefaultService(BaseService):
    def __init__(self, args):
        try:
            super().__init__(args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self._logic = type(self).LOGIC()  # bruh
        except BaseException:
            logging.exception("")
            raise

    def SvcDoRun(self):
        logging.info("running service")
        try:
            # run user logic until yield is reached
            self._logic.send(None)
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        except Exception:
            logging.exception("")

    def SvcStop(self):
        logging.info("exiting")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        with contextlib.suppress(Exception):
            win32event.SetEvent(self.hWaitStop)
            # run user logic after yield (usually should be cleanup)
            self._logic.send(None)
        logging.info("exited")


@contextlib.contextmanager
def tmp_change(cls: object, field_name: str, new_value: object):
    should_del = hasattr(cls, field_name)
    old_value = getattr(cls, field_name, object)
    setattr(cls, field_name, new_value)
    try:
        yield
    finally:
        if should_del and hasattr(cls, field_name):
            delattr(cls, field_name)
            return
        setattr(cls, field_name, old_value)


@dataclass
class ServiceData(Generic[_B]):
    name: str
    display_name: str
    entrypoint: str
    logic: Callable
    svc_class: _B

    @contextlib.contextmanager
    def set_service(self) -> ContextManager[_B]:
        with contextlib.ExitStack() as stack:
            stack.enter_context(tmp_change(self.svc_class, "_svc_name_", self.name))
            stack.enter_context(
                tmp_change(self.svc_class, "_svc_display_name_", self.display_name)
            )
            stack.enter_context(
                tmp_change(self.svc_class, "_svc_entrypoint_", self.entrypoint)
            )
            stack.enter_context(tmp_change(self.svc_class, "LOGIC", self.logic))
            yield self.svc_class


def entrypoint(service_data: ServiceData[_B]):
    def wrapper():
        with service_data.set_service() as service:
            service: Type[BaseService]
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(service)
            servicemanager.StartServiceCtrlDispatcher()
    return wrapper
