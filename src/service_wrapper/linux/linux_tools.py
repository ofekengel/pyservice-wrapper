from dataclasses import dataclass
from pathlib import Path

from service_wrapper.linux.linux_wrapper import ServiceData
from service_wrapper.linux.systemd import Options, SystemdCtl
from service_wrapper.utils.service_tools import IServiceTools


@dataclass
class ServiceTools(IServiceTools[ServiceData[None]]):
    service: ServiceData[None]

    def __post_init__(self):
        self.ctl = SystemdCtl(self.service.name)

    def start_service(self):
        self.ctl.run(Options.start)

    def stop_service(self):
        self.ctl.run(Options.stop)

    def install_service(self, binary_path: Path):
        unit_data = (
            Path(__file__)
            .parent.joinpath("template.service")
            .read_text()
            .format(name=self.service.name, binary=binary_path)
        )
        Path(f"/etc/systemd/system/{self.service.name}.service").write_text(unit_data)
        self.ctl.reload()

    def uninstall_service(self):
        self.ctl.run(Options.stop)
        Path(f"/etc/systemd/system/{self.service.name}.service").unlink(missing_ok=True)
        self.ctl.reload()


""""""
