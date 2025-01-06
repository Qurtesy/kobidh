import click
from click import echo
from kobidh.core import some_function

@click.group()
def main():
    pass

@main.command()
def test():
    echo(some_function())