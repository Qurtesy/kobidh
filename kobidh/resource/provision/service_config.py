import boto3
from kobidh.utils.format import camelcase
from troposphere.ecs import (
    TaskDefinition,
    PortMapping,
    ContainerDefinition,
    Service,
    DeploymentConfiguration,
    NetworkConfiguration,
    AwsvpcConfiguration,
    Environment,
)
from troposphere import Ref
from kobidh.utils.logging import log, log_err
from kobidh.resource.config import Config, StackOutput


class ServiceConfig:
    def __init__(self, config: Config, stack_op: StackOutput):
        self.config = config
        self.stack_op = stack_op
        self.task_definition = camelcase(f"{self.config.name}-td")
        self.task_definition_family = camelcase(f"{self.config.name}-task")
        self.service_name = camelcase(f"{self.config.name}-service")

    def _configure(self):
        try:
            container_port = 80
            # ECS Task Definition
            task_definition = TaskDefinition(
                camelcase(self.task_definition),
                Family=self.task_definition_family,
                Cpu="256",
                Memory="512",
                NetworkMode="awsvpc",
                ExecutionRoleArn=boto3.resource("iam").Role("ecsTaskExecutionRole").arn,
                ContainerDefinitions=[
                    ContainerDefinition(
                        Name=camelcase(f"{self.config.name}-web"),
                        Image=f"{self.stack_op.ecr_uri}:latest",
                        Cpu=256,
                        Memory=512,
                        Essential=True,
                        PortMappings=[
                            PortMapping(
                                "HttpPortMapping",
                                ContainerPort=container_port,
                                HostPort=80,
                                Protocol="tcp",
                            )
                        ],
                        # Initial environment configuration
                        Environment=[
                            Environment(Name="PORT", Value=str(container_port))
                        ],
                    )
                ],
            )
            self.config.template.add_resource(task_definition)

            # Log Task Definition information
            log("Task Definition configiuration added")
            log(f"Task Definition family name: {self.task_definition_family}")
            log(f"Task Definition image uri: {self.stack_op.ecr_uri}")

            launch_type = "EC2"
            service = Service(
                camelcase(f"{self.config.name}-service"),
                Cluster=self.stack_op.ecs_cluster_name,
                DeploymentConfiguration=DeploymentConfiguration(
                    MinimumHealthyPercent=100, MaximumPercent=200
                ),
                LaunchType=launch_type,
                NetworkConfiguration=NetworkConfiguration(
                    AwsvpcConfiguration=AwsvpcConfiguration(
                        Subnets=self.stack_op.public_subnet_names.split(":"),
                        SecurityGroups=[self.stack_op.security_group_name],
                    )
                ),
                DesiredCount=1,  # Specify the number of tasks to launch
                ServiceName=camelcase(f"{self.config.name}-service"),
                TaskDefinition=Ref(task_definition),
            )
            self.config.template.add_resource(service)

            # Log ECS Service information
            log(f'ECS Service configiuration added for "{launch_type}"')

        except Exception as e:
            log_err(str(e))
