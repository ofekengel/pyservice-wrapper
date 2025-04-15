from invoke import Context, task


@task()
def lint(c: Context):
    c.run("black -l 88 .")
    c.run("isort --profile black .")


@task(lint)
def build(ctx: Context):
    ctx.run("pdm build --no-sdist")


@task(build)
def dev_upload(ctx: Context, port: int = 6060):
    print(port)
    ctx.run(
        f"twine upload "
        f"--non-interactive --disable-progress-bar -u a -p b "
        f"--repository-url http://localhost:{port} dist/*"
    )
