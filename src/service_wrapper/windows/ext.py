import contextlib
import logging
import os
import signal
from multiprocessing import Process
from typing import Callable

import win32service

from service_wrapper.windows.base_service import BaseService

Logger = logging.Logger("BlockingService")


class BlockingService(BaseService):
    LOGIC: Callable

    def __init__(self, args):
        super().__init__(args)
        Logger.info("initializing service")
        self.process = Process(target=self.LOGIC)

    def SvcDoRun(self):
        Logger.info("running service")
        try:
            # run user logic until yield is reached
            self.process.start()
            self.process.join()  # todo: is ok after kill?
        except Exception:
            logging.exception("")

    def SvcStop(self):
        Logger.info("exiting")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        with contextlib.suppress(Exception):
            os.kill(self.process.pid, signal.SIGINT)
        Logger.info("exited")
