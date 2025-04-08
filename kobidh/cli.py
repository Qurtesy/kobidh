import functools
import click
from kobidh.core import Core, Apps, Service, Container

@click.group()
def main():
    """CLI tool for automating the containerized application deployment process"""
    pass


# --------------------
# Core Commands
# --------------------
@main.command()
def setup():
    Core().setup()

@main.command()
def show():
    Core().show()


# --------------------
# Apps Commands
# --------------------
@main.command(name="apps.create")
@click.argument("name", type=str)
def apps_create(name):
    Apps(name).create()

@main.command(name="apps.describe")
@click.argument("name", type=str)
def apps_describe(name):
    Apps(name).describe()

@main.command(name="apps.info")
@click.argument("name", type=str)
def apps_info(name):
    Apps(name).info()

@main.command(name="apps.delete")
@click.argument("name", type=str)
def apps_delete(name):
    Apps(name).delete()


# --------------------
# Service Commands
# --------------------
@main.command(name="service.create")
@click.argument("name", type=str)
def service_create(name):
    Service(name).create()

@main.command(name="service.delete")
@click.argument("name", type=str)
def service_delete(name):
    Service(name).delete()


# (heroku container:push web)
@main.command(name="container:push")
@click.argument("name", type=str)
def container_push(name):
    Container(name).push()
