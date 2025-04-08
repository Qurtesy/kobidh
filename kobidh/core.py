import os
import boto3
import logging
from click import echo, prompt
from kobidh.meta import DIR, DEFAULT_FILE
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
    @aws_credentails
    def __init__(self, name: str, region: str = None):
        self.name = name
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    def create(self):
        try:
            echo(f'Creating app "{self.name}" for "{self.region}"..')
            config = Infra.configure(self.name, self.region)
            echo(f'App "{self.name}" configuration created..')
            Infra.apply(config.name, config.region, config.template)
            echo(f'App "{self.name}" configuration is applied..')
        except Exception as e:
            log_err(str(e))

    def describe(self):
        Infra.describe(self.name, self.region)

    def info(self):
        Infra.info(self.name, self.region)

    def delete(self):
        echo(f'Deleting app "{self.name}"..')
        Infra.delete(self.name, self.region)


class Service:
    @aws_credentails
    def __init__(self, app: str, region: str = None):
        self.app = app
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    def create(self):
        try:
            echo(f'Provisioning app "{self.app}"..')
            config = Provision.configure(self.app, self.region)
            Provision.apply(config)
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
        Provision.push(self.app, self.region)
