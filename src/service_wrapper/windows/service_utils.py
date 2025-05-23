import contextlib
import logging
import os
import sys
from pathlib import Path
from typing import ContextManager, Type, TypeVar

import servicemanager
import win32event
import win32service

from service_wrapper.utils.utils import ServiceData
from service_wrapper.windows.base_service import BaseService

_T = TypeVar("_T")
_B = TypeVar("_B", bound=Type[BaseService])


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
def tmp_change(cls: Type, field_name: str, new_value: object):
    should_del = not hasattr(cls, field_name)
    old_value = getattr(cls, field_name, object)
    setattr(cls, field_name, new_value)
    try:
        yield
    finally:
        if should_del and hasattr(cls, field_name):
            delattr(cls, field_name)
            return
        setattr(cls, field_name, old_value)


@contextlib.contextmanager
def set_service(service_data: ServiceData[_B]) -> ContextManager[_B]:
    with (
        tmp_change(service_data.svc_class, "_svc_name_", service_data.name),
        tmp_change(
            service_data.svc_class,
            "_svc_display_name_",
            service_data.display_name,
        ),
        tmp_change(service_data.svc_class, "_svc_entrypoint_", service_data.entrypoint),
        tmp_change(service_data.svc_class, "LOGIC", service_data.logic),
    ):
        yield service_data.svc_class


@contextlib.contextmanager
def patch_cwd() -> ContextManager[None]:
    cwd = Path.cwd()
    try:
        os.chdir(Path(sys.executable).parent)
        yield
    finally:
        os.chdir(cwd)


def entrypoint(service_data: ServiceData[_B]):
    def wrapper():
        with patch_cwd():
            with set_service(service_data) as service:
                service: Type[BaseService]
                servicemanager.Initialize()
                servicemanager.PrepareToHostSingle(service)
                servicemanager.StartServiceCtrlDispatcher()

    return wrapper
