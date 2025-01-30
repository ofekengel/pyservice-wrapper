import contextlib
import os
from pathlib import Path

from pdm.backend.hooks.base import Context

import src


def get_excluded_module():
    if os.name == "nt":
        with contextlib.suppress(ImportError):
            from src.service_wrapper import linux

            return linux
        return None
    else:
        with contextlib.suppress(ImportError):
            from src.service_wrapper import windows

            return windows
        return None


def get_root() -> Path | None:
    module = get_excluded_module()
    if module is not None:
        return Path(module.__file__).parent


def pdm_build_initialize(context: Context):
    root = get_root()
    if root is None:
        return
    # weird behavior where build_tools are already excluded but initialize runs again
    source = Path(src.__file__).parent.parent
    context.config.build_config.setdefault("excludes", [])
    context.config.build_config["excludes"].append(
        str(root.relative_to(source).joinpath("*")),
    )
