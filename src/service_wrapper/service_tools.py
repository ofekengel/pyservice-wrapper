import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Type

import win32api
import win32service
import win32serviceutil
import winerror

from service_wrapper.service_wrapper import ServiceData
from service_wrapper.base_service import BaseService


@dataclass
class ServiceTools:
    service: ServiceData[Type[BaseService]]

    def start_service(self):
        with self.service.set_service():
            win32serviceutil.StartService(self.service.name)
            time.sleep(5)  # fixme: needed?
            win32serviceutil.WaitForServiceStatus(
                self.service.name, win32service.SERVICE_RUNNING, 1
            )

    def stop_service(self):
        with self.service.set_service():
            try:
                win32serviceutil.StopService(self.service.name)
            except win32api.error as e:
                if e.winerror != winerror.ERROR_SERVICE_NOT_ACTIVE:
                    raise
            win32serviceutil.WaitForServiceStatus(
                self.service.name, win32service.SERVICE_STOPPED, 1
            )

    def install_service(self, exe_path: Path):
        with self.service.set_service():
            logging.info(win32serviceutil.GetServiceClassString(self.service.svc_class))
            logging.info(str(exe_path))
            win32serviceutil.InstallService(
                pythonClassString=win32serviceutil.GetServiceClassString(
                    self.service.svc_class),
                exeName=str(exe_path),
                serviceName=self.service.name,
                displayName=self.service.display_name,
                startType=win32service.SERVICE_AUTO_START,
                exeArgs=self.service.entrypoint,
            )
            self.start_service()

    def uninstall_service(self):
        with self.service.set_service():
            self.stop_service()
            win32serviceutil.RemoveService(self.service.name)
