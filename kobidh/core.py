import os
import boto3
import logging
from typing import Optional, Dict, Any
from click import echo, prompt
from kobidh.meta import DIR, DEFAULT_FILE
from kobidh.exceptions import KobidhError, ConfigurationError, AWSError, DeploymentError
from kobidh.resource.infra import Infra
from kobidh.resource.provision import Provision
from kobidh.utils.logging import log_err
from kobidh.utils.decorators import aws_credentails

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.home_dir = os.path.expanduser("~")
        self.kobidh_config = os.path.join(self.home_dir, DIR)

        self.app = None
        self.region = None

    def parse(content: str) -> dict:
        config = dict()
        if not content:
            return config
        attributes: list[str] = content.split("\n")
        for attr in attributes:
            if not attr:
                return config
            parts: list[str] = attr.split(":")
            config[parts[0].strip()] = parts[1].strip()
        return config

    def serialize(config: dict) -> str:
        content = ""
        for k, v in config.items():
            content += f"{k}:{v}\n"
        return content

    def get_config(self):
        os.makedirs(self.kobidh_config, exist_ok=True)
        file = None
        try:
            file = open(os.path.join(self.home_dir, f"{DIR}/{DEFAULT_FILE}"), "r")
            config = Config.parse(file.read())
        except FileNotFoundError as e:
            echo(f"Configuration not found. Setting it up...")
            config = {}
        finally:
            if self.app:
                config["app"] = self.app
            if self.region:
                config["region"] = self.region
            content: str = Config.serialize(config)
            file = open(os.path.join(self.home_dir, f"{DIR}/{DEFAULT_FILE}"), "w")
            file.write(content)
            file.close()
        return config


class Core:
    @aws_credentails
    def __init__(self):
        self.session = boto3.session.Session()
        self.config = Config()

    def setup(self):
        self.config.app = prompt("application")
        self.config.region = prompt("region", default=self.session.region_name)
        self.config.get_config()

    def show(self):
        echo()
        echo(f"Configuration:")
        echo(f"--------------------------------------------------------------")
        for k, v in self.config.get_config().items():
            echo(f"{k}: {v}")
        echo()


class Apps:
    """Application management for Kobidh deployment automation."""

    @aws_credentails
    def __init__(self, name: str, region: Optional[str] = None):
        """
        Initialize Apps manager.

        Args:
            name: Application name
            region: AWS region (optional)

        Raises:
            ConfigurationError: If application name is invalid
        """
        if not name or not name.strip():
            raise ConfigurationError(
                "Application name cannot be empty", "Provide a valid application name"
            )

        self.name = name.strip()
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

        logger.info(
            f"Apps manager initialized for '{self.name}' in region '{self.region}'"
        )

    def create(self):
        """Create application infrastructure with enhanced error handling."""
        try:
            logger.info(f"Creating infrastructure for app '{self.name}'")
            echo(f'🚀 Creating app "{self.name}" for "{self.region}"..')

            config = Infra.configure(self.name, self.region)
            echo(f'✅ App "{self.name}" configuration created..')

            Infra.apply(config.name, config.region, config.template)
            echo(f'✅ App "{self.name}" infrastructure deployed successfully!')

            logger.info(f"Successfully created app '{self.name}'")

        except Exception as e:
            logger.error(f"Failed to create app '{self.name}': {str(e)}")
            if isinstance(e, KobidhError):
                raise
            raise DeploymentError(
                f"Failed to create app '{self.name}': {str(e)}",
                suggestion="Check CloudFormation console for detailed error information",
            )

    def describe(self):
        """Describe application infrastructure details."""
        try:
            logger.info(f"Describing app '{self.name}'")
            Infra.describe(self.name, self.region)
        except Exception as e:
            logger.error(f"Failed to describe app '{self.name}': {str(e)}")
            if "does not exist" in str(e).lower():
                raise DeploymentError(
                    f"App '{self.name}' not found",
                    suggestion="Use 'kobidh apps.create' to create the application first",
                )
            raise AWSError(f"Failed to describe app: {str(e)}")

    def info(self):
        """Show application information."""
        try:
            logger.info(f"Getting info for app '{self.name}'")
            Infra.info(self.name, self.region)
        except Exception as e:
            logger.error(f"Failed to get info for app '{self.name}': {str(e)}")
            if "does not exist" in str(e).lower():
                raise DeploymentError(
                    f"App '{self.name}' not found",
                    suggestion="Use 'kobidh apps.create' to create the application first",
                )
            raise AWSError(f"Failed to get app info: {str(e)}")

    def delete(self):
        """Delete application and all associated resources."""
        try:
            logger.info(f"Deleting app '{self.name}'")
            echo(f'🗑️ Deleting app "{self.name}"..')

            Infra.delete(self.name, self.region)
            echo(f'✅ App "{self.name}" deleted successfully!')

            logger.info(f"Successfully deleted app '{self.name}'")

        except Exception as e:
            logger.error(f"Failed to delete app '{self.name}': {str(e)}")
            if isinstance(e, KobidhError):
                raise
            raise DeploymentError(
                f"Failed to delete app '{self.name}': {str(e)}",
                suggestion="Check CloudFormation console and manually clean up resources if needed",
            )


class Service:
    @aws_credentails
    def __init__(self, app: str, region: str = None):
        self.app = app
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    def create(self):
        try:
            echo(f'Provisioning app "{self.app}"..')
            provision = Provision(self.app, self.region)
            provision.configure()
            provision.apply()
        except Exception as e:
            log_err(str(e))

    def delete(self):
        echo(f'Removing app "{self.app}" provision..')
        Provision.delete(self.app, self.region)


class Container:
    @aws_credentails
    def __init__(self, app: str, region: str = None):
        self.app = app
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    def push(self):
        Provision.push(self.app)

    def release(self):
        Provision.release(self.app)
