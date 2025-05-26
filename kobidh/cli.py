import functools
import click
import logging
import sys
from kobidh.core import Core, Apps, Service, Container
from kobidh.exceptions import KobidhError

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """Decorator to handle exceptions gracefully."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KobidhError as e:
            click.echo(f"❌ Error: {e.message}", err=True)
            if e.suggestion:
                click.echo(f"💡 Suggestion: {e.suggestion}", err=True)
            sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\n❌ Operation cancelled by user", err=True)
            sys.exit(130)
        except Exception as e:
            click.echo(f"❌ Unexpected error: {str(e)}", err=True)
            logger.exception("Unexpected error")
            sys.exit(1)

    return wrapper


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.version_option(version="1.0.0", prog_name="kobidh")
def main(verbose):
    """🚀 Kobidh - CLI tool for automating containerized application deployment"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    logger.info("Kobidh CLI started")


# --------------------
# Core Commands
# --------------------
@main.command()
@handle_exceptions
def setup():
    """🔧 Initial setup and configuration"""
    click.echo("🔧 Starting Kobidh setup...")
    Core().setup()


@main.command()
@handle_exceptions
def show():
    """📋 Show current configuration"""
    Core().show()


# --------------------
# Apps Commands
# --------------------
@main.command(name="apps.create")
@click.argument("name", type=str)
@click.option("--region", "-r", help="AWS region to deploy to")
@handle_exceptions
def apps_create(name, region):
    """🏗️ Create application infrastructure"""
    click.echo(f"🏗️ Creating application '{name}'...")
    Apps(name, region).create()


@main.command(name="apps.describe")
@click.argument("name", type=str)
@click.option("--region", "-r", help="AWS region")
@handle_exceptions
def apps_describe(name, region):
    """📊 Describe application infrastructure details"""
    Apps(name, region).describe()


@main.command(name="apps.info")
@click.argument("name", type=str)
@click.option("--region", "-r", help="AWS region")
@handle_exceptions
def apps_info(name, region):
    """ℹ️ Show application information"""
    Apps(name, region).info()


@main.command(name="apps.delete")
@click.argument("name", type=str)
@click.option("--region", "-r", help="AWS region")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@handle_exceptions
def apps_delete(name, region, force):
    """🗑️ Delete application and all resources"""
    if not force:
        if not click.confirm(
            f"⚠️ Are you sure you want to delete app '{name}' and ALL its resources?"
        ):
            click.echo("❌ Deletion cancelled")
            return
    click.echo(f"🗑️ Deleting application '{name}'...")
    Apps(name, region).delete()


# --------------------
# Service Commands
# --------------------
@main.command(name="service.create")
@click.argument("name", type=str)
@click.option("--region", "-r", help="AWS region")
@handle_exceptions
def service_create(name, region):
    """🚀 Create and deploy ECS service"""
    click.echo(f"🚀 Creating service for app '{name}'...")
    Service(name, region).create()


@main.command(name="service.delete")
@click.argument("name", type=str)
@click.option("--region", "-r", help="AWS region")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@handle_exceptions
def service_delete(name, region, force):
    """🗑️ Delete ECS service"""
    if not force:
        if not click.confirm(
            f"⚠️ Are you sure you want to delete service for app '{name}'?"
        ):
            click.echo("❌ Deletion cancelled")
            return
    click.echo(f"🗑️ Deleting service for app '{name}'...")
    Service(name, region).delete()


# --------------------
# Container Commands
# --------------------
@main.command(name="container.push")
@click.argument("name", type=str)
@click.option("--region", "-r", help="AWS region")
@handle_exceptions
def container_push(name, region):
    """📦 Build and push container to ECR"""
    click.echo(f"📦 Building and pushing container for app '{name}'...")
    Container(name, region).push()
