import boto3
import logging
from stringcase import camelcase
from botocore.exceptions import ClientError
from kobidh.resource.config import Config
from kobidh.resource.vpc_config import VPCConfig
from kobidh.resource.iam_config import IAMConfig
from kobidh.resource.autoscaling_config import AutoScalingConfig
from kobidh.resource.ecr_config import ECRConfig
from kobidh.resource.ecs_config import ECSConfig

logger = logging.getLogger(__name__)


class Configuration:

    @staticmethod
    def configure(name: str, region: str = None) -> Config:
        config = Config(name, region)

        vpc_config = VPCConfig(config)
        vpc_config._configure()

        iam_config = IAMConfig(config)
        iam_config._configure()

        ecr_config = ECRConfig(config)
        ecr_config._configure()

        ecs_config = ECSConfig(config, vpc_config, ecr_config)
        ecs_config._configure()

        asg_config = AutoScalingConfig(config, vpc_config, iam_config, ecs_config)
        asg_config._configure()

        return config

    @staticmethod
    def apply(config: Config):
        cloud_client = boto3.client("cloudformation", region_name=config.region)
        stack_name = camelcase(f"{config.name}AppStack".replace("-", "_"))
        response = None
        try:
            # Check if the stack exists
            stacks = cloud_client.describe_stacks(StackName=stack_name)
            logger.info(stacks)
            logger.info(f"Stack {stack_name} exists. Updating it...")

            # Update the existing stack
            response = cloud_client.update_stack(
                StackName=stack_name,
                TemplateBody=config.template.to_json(),
                Capabilities=["CAPABILITY_NAMED_IAM"],
            )
            logger.info(f"Stack update initiated: {response['StackId']}")

        except ClientError as e:
            # If stack does not exist, create it
            if "does not exist" in str(e):
                logger.info(f"Stack {stack_name} does not exist. Creating it...")
                response = cloud_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=config.template.to_json(),
                    Capabilities=["CAPABILITY_NAMED_IAM"],
                )
                logger.info(f"Stack creation initiated: {response['StackId']}")
            elif "No updates are to be performed" in str(e):
                logger.warning(f"No updates are to be performed!")
            else:
                logger.error(f"Unexpected error: {e}")
                raise
        return response

    @staticmethod
    def delete(name: str, region: str):
        cloud_client = boto3.client("cloudformation", region_name=region)
        stack_name = camelcase(f"{name}AppStack".replace("-", "_"))
        response = cloud_client.delete_stack(StackName=stack_name)
        logger.info(response)
        return response
