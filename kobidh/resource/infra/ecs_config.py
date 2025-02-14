from troposphere import Ref, Output
from troposphere.ecs import Cluster
from kobidh.utils.format import camelcase
from kobidh.resource.infra.attrs import Attrs
from kobidh.resource.config import Config


class ECSConfig:
    """
    Contains ECS configuration details
    """

    def __init__(self, config: Config):
        self.config = config
        self.attrs = Attrs(self.config.name)
        self.ecs_cluster = None

    def _configure(self):
        # ECS Cluster
        self.ecs_cluster = Cluster(camelcase(self.attrs.cluster_name))
        self.config.template.add_resource(self.ecs_cluster)
        self.config.template.add_output(
            Output(
                "ClusterName",
                Description="The name of the cluster",
                Value=Ref(self.ecs_cluster),
            )
        )
