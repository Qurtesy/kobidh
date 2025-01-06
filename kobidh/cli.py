import functools
import click
from kobidh.core import Apps


@click.group()
def main():
    pass


def _region(func):
    @click.option("--region", "-r", help="region", required=False)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# kobidh apps.create fastapi-basicapp
@main.command(name="apps.create")
@_region
@click.argument("name", type=str)
def apps_create(name, region):
    Apps(name).create()
