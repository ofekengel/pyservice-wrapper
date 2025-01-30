import contextlib

with contextlib.suppress(
    ImportError
):  # for build time imports, should not happen in production!
    from service_wrapper.wrapper import as_service, get_service_tools

# only expose these functions on developer import
