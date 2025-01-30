# Service Wrapper

A python tool to easily create services running under the os's service management
[[source code](https://github.com/ofekengel/pyservice-wrapper)]

## Function as a service
Make a script into a service running under Windows's scm (linux WIP) 
using a simple decorator.

Intended to work with [PyInstaller](https://pyinstaller.org/en/stable/) 
(or alternatives) to create an executable that can be registered under scm.

`python main.py` still works. Function will block until `KeyboardInterrupt` is received.

`main.py`

```python
from service_wrapper.windows import as_service


@as_service(SERVICE_NAME, SERVICE_DISPLAY_NAME, SERVICE_ENTRYPOINT_COMMAND)
def main():
    startup()
    try:
        yield
    finally:
        cleanup()


if __name__ == "__main__":
    main()
```

#### NOTES:
- The decorated function should not accept arguments
- `startup` should be non-blocking (open threads/processes).
- For blocking functions look at [Blocking Functions](#blocking-functions)

### Blocking functions

----
It is recommended to use a Generator as the decorated function but not required.
In order to decorate a blocking function:

```python
from service_wrapper.windows import as_service
from service_wrapper.windows import BlockingService


@as_service(
    SERVICE_NAME,
    SERVICE_DISPLAY_NAME,
    SERVICE_ENTRYPOINT_COMMAND,
    base=BlockingService,
)
def main():
    run_logic()


if __name__ == "__main__":
    main()

```
#### NOTES:
- When invoked using scm (PyInstalled and installed as a service), `BlockingService`
will run `main()` is a separate spawned process.
- SIGINT will be sent to that process the scm stop is called

## Service Tooling
Controls for installing\removing the service are provided using the `ServiceTools`.

They are to be used externally in scripts to streamline installation\removal etc.

For example, usage in CI with a tool like [invoke](https://www.pyinvoke.org/)

```python
from pathlib import Path

from invoke import Context, task

from service_wrapper.windows import get_service
from service_wrapper.windows.service_tools import ServiceTools

service_tools = ServiceTools(get_service(main))

EXECUTABLE_PATH = Path("./dist/svc.exe")


@task()
def build(context: Context) -> None:
    context.run(
        f"pyinstaller "
        f"--onefile "
        f"--name=svc "
        f"main.py"
    )


@task(build)
def install(_: Context) -> None:
    service_tools.install_service(EXECUTABLE_PATH)


@task
def restart(_: Context) -> None:
    service_tools.stop_service()
    service_tools.start_service()

```



