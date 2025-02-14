import functools
import click
from kobidh.core import Core, Apps, Service, Container


@click.group()
def main():
    pass


def _app(func):
    @click.option("--app", "-a", help="app", required=False)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def _region(func):
    @click.option("--region", "-r", help="region", required=False)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# kobidh setup
@main.command()
def setup():
    Core().setup()


# kobidh show
@main.command()
def show():
    Core().show()


# kobidh apps.create tomato
@main.command(name="apps.create")
@click.argument("name", type=str)
def apps_create(name):
    Apps(name).create()


# kobidh apps.describe tomato
@main.command(name="apps.describe")
@click.argument("name", type=str)
def apps_describe(name):
    Apps(name).describe()


# kobidh apps.delete tomato
@main.command(name="apps.delete")
@click.argument("name", type=str)
def apps_delete(name):
    Apps(name).delete()


# kobidh service.create (heroku container:push web)
@main.command(name="service.create")
@click.argument("name", type=str)
def service_create(name):
    Service(name).create()


# kobidh service.delete tomato
@main.command(name="service.delete")
@click.argument("name", type=str)
def service_create(name):
    Service(name).delete()


# (heroku container:push web)
@main.command(name="container:push")
@click.argument("name", type=str)
def container_push(name):
    Container(name).push()
