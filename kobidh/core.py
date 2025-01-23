import boto3
import boto3.session
from click import echo
from kobidh.service.configuration import Configuration


class Apps:
    def __init__(self, name: str, region: str = None):
        self.name = name
        self.session = boto3.session.Session()
        self.region = region if region else self.session.region_name

    def configure(self):
        echo("Configuring VPC Resources...")
        pass

    def create(self):
        echo(f'Creating app "{self.name}"..')
        config = Configuration.configure(self.name, self.region)
        Configuration.apply(config)
        pass

    def delete(self):
        echo(f'Deleting app "{self.name}"..')
        Configuration.delete(self.name, self.region)
        pass
