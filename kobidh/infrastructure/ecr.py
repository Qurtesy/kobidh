from troposphere import GetAtt, Output
from troposphere.ecr import Repository
from kobidh.utils.format import camelcase
from kobidh.resource.config import Config


class ECRConfig:
    """
    Contains Elastic Container Registry configuration details
    """

    def __init__(self, config: Config):
        self.config = config
        self.default_service = "web"
        self.ecr = None

    def _configure(self):
        self.ecr = Repository(
            camelcase(self.config.attrs.ecr_name),
            RepositoryName=f"{self.config.attrs.ecr_name}/{self.default_service}",  # Change to your desired repository name
        )
        self.config.template.add_resource(self.ecr)
        self.config.template.add_output(
            Output(
                "ECRUri",
                Description="The uri of the container registry",
                Value=GetAtt(self.ecr, "RepositoryUri"),
            )
        )
