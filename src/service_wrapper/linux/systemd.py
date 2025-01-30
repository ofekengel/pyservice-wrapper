import subprocess
from dataclasses import dataclass
from enum import StrEnum
from subprocess import Popen


class Options(StrEnum):
    start = "start"
    stop = "stop"
    restart = "restart"


@dataclass
class SystemdCtl:
    name: str

    @staticmethod
    def _run(cmd: str):
        with Popen(
            f"systemctl {cmd}",
            encoding="utf-8",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as p:
            (stdout, stderr) = p.communicate()
            ret_code = p.poll()
            if ret_code == 1:
                raise SystemError(stderr)
        return

    def reload(self):
        self._run("daemon-reload")

    def run(self, option: Options):
        self._run(f"{option} {self.name}")
