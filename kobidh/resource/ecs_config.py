from stringcase import camelcase
from troposphere import Ref
from troposphere.ecs import Cluster, TaskDefinition, PortMapping, ContainerDefinition
from .config import Config
from .vpc_config import VPCConfig
from .ecr_config import ECRConfig


class ECSConfig:
    """
    Contains ECS configuration details
    """

    def __init__(self, config: Config, vpc_config: VPCConfig, ecr_config: ECRConfig):
        self.config = config
        self.vpc_config = vpc_config
        self.ecr_config = ecr_config
        self.task_definition_name = f"{self.config.name}-task-definition"
        self.container_name = f"{self.config.name}-container"
        self.cluster_name = f"{self.config.name}-cluster"
        self.ecs_td_name = f"{self.config.name}-td"
        self.ecs_service_name = f"{self.config.name}-service"
        self.ecs_cluster = None

    def _configure(self):
        # ECS Cluster
        self.ecs_cluster = Cluster(camelcase(self.cluster_name.replace("-", "_")))
        self.config.template.add_resource(self.ecs_cluster)

        # ECS Task Definition
        task_definition = TaskDefinition(
            camelcase(self.ecs_td_name.replace("-", "_")),
            Family=self.task_definition_name,
            ContainerDefinitions=[
                ContainerDefinition(
                    Name=camelcase(self.container_name.replace("-", "_")),
                    Image=Ref(self.ecr_config.ecr),  # Replace with your image
                    Memory=512,
                    Cpu=256,
                    Essential=True,
                    PortMappings=[PortMapping("MyPortMapping", ContainerPort=80)],
                )
            ],
        )
        self.config.template.add_resource(task_definition)
