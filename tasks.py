from argparse import ArgumentParser

from pyshell.main import CLIApp, Context

cli = CLIApp()


@cli.task()
def lint(c: Context):
    c.run("black -l 88 .")
    c.run("isort --profile black .")


@cli.task(lint)
def build(ctx: Context):
    ctx.run("pdm build --no-sdist")


parser = ArgumentParser()
parser.add_argument("--port", type=int, default=6060)


@cli.task(build, parser=parser)
def dev_upload(ctx: Context):
    ctx.run(
        f"twine upload "
        f"--non-interactive --disable-progress-bar -u a -p b "
        f"--repository-url http://localhost:{ctx.namespace.port} dist/*"
    )
