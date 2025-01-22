import contextlib
import logging
from typing import Callable, Protocol, Type, TypeVar

import servicemanager
import win32event
import win32service

from service_wrapper.base_service import BaseService

_T = TypeVar("_T")


class ServiceFunction(Protocol[_T]):
    __service__: _T

    def __call__(self) -> ...: ...


class DefaultService(BaseService):
    def __init__(self, args):
        super().__init__(args)
        self.Logger = logging.Logger(type(self).name)
        self.Logger.info("initializing service")
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self._logic = self.LOGIC()

    def SvcDoRun(self):
        self.Logger.info("running service")
        try:
            # run user logic until yield is reached
            self._logic.send(None)
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        except Exception:
            logging.exception("")

    def SvcStop(self):
        self.Logger.info("exiting")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        with contextlib.suppress(Exception):
            win32event.SetEvent(self.hWaitStop)
            # run user logic after yield (usually should be cleanup)
            self._logic.send(None)
        self.Logger.info("exited")


def entrypoint(service: Type[BaseService]):
    def wrapper():
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(service)
        servicemanager.StartServiceCtrlDispatcher()

    return wrapper
