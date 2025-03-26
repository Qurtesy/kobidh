import os
import boto3
import botocore
import logging
from click import echo, prompt
from kobidh.meta import DIR, DEFAULT_FILE
from kobidh.resource.infra import Infra
from kobidh.resource.provision import Provision
from kobidh.utils.logging import log_err

logger = logging.getLogger(__name__)

def aws_credentails(func):
    def wrapper(*args, **kwargs):
        try:
            session = boto3.Session()
            credentials = session.get_credentials()

            if credentials is None:
                raise Exception("AWS credentials not found. Run `aws configure` to set them up.")
            
            client = session.client("sts")
            identity = client.get_caller_identity()
            echo(f"AWS credentials are set up correctly. Account ID: {identity['Account']}")

        except botocore.exceptions.NoCredentialsError:
            raise Exception("No AWS credentials found. Run `aws configure` to set them up.")
        except botocore.exceptions.PartialCredentialsError:
            raise Exception("Incomplete AWS credentials found. Please check your AWS configuration.")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        return func(*args, **kwargs)
    return wrapper


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
    def __init__(self):
        self.session = boto3.session.Session()
        self.config = Config()

    @aws_credentails
    def setup(self):
        self.config.app = prompt("application")
        self.config.region = prompt("region", default=self.session.region_name)
        self.config.get_config()

    @aws_credentails
    def show(self):
        echo()
        echo(f"Configuration:")
        echo(f"--------------------------------------------------------------")
        for k, v in self.config.get_config().items():
            echo(f"{k}: {v}")
        echo()


class Apps:
    def __init__(self, name: str, region: str = None):
        self.name = name
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    @aws_credentails
    def create(self):
        try:
            echo(f'Creating app "{self.name}" for "{self.region}"..')
            config = Infra.configure(self.name, self.region)
            echo(f'App "{self.name}" configuration created..')
            Infra.apply(config.name, config.region, config.template)
            echo(f'App "{self.name}" configuration is applied..')
        except Exception as e:
            log_err(str(e))

    @aws_credentails
    def describe(self):
        Infra.describe(self.name, self.region)

    def info(self):
        Infra.info(self.name, self.region)

    def delete(self):
        echo(f'Deleting app "{self.name}"..')
        Infra.delete(self.name, self.region)


class Service:
    def __init__(self, app: str, region: str = None):
        self.app = app
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    @aws_credentails
    def create(self):
        try:
            echo(f'Provisioning app "{self.app}"..')
            config = Provision.configure(self.app, self.region)
            Provision.apply(config)
        except Exception as e:
            log_err(str(e))

    @aws_credentails
    def delete(self):
        echo(f'Removing app "{self.app}" provision..')
        Provision.delete(self.app, self.region)


class Container:
    def __init__(self, app: str, region: str = None):
        self.app = app
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    @aws_credentails
    def push(self):
        Provision.push(self.app, self.region)
