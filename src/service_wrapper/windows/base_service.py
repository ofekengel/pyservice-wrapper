from typing import Callable, Generator

import win32serviceutil


class ClassProperties(type):
    _svc_name_: str
    _svc_display_name_: str
    _svc_entrypoint_: str

    @property
    def name(cls):
        return cls._svc_name_

    @property
    def display_name(cls):
        return cls._svc_display_name_

    @property
    def entrypoint(cls):
        return cls._svc_entrypoint_


class BaseService(win32serviceutil.ServiceFramework, metaclass=ClassProperties):
    """
    Implement your own logic for service lifecycle the same way you would with
    `win32serviceutil.ServiceFramework` (mainly `SvcDoRun`, `SvcStop`).
    """

    # todo: something that is not generator?
    LOGIC: Callable[[], Generator]
