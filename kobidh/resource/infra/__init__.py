import boto3
from kobidh.utils.format import camelcase
from botocore.exceptions import ClientError
from kobidh.resource.config import Config
from kobidh.resource.infra.vpc_config import VPCConfig
from kobidh.resource.infra.iam_config import IAMConfig
from kobidh.resource.infra.ecr_config import ECRConfig
from kobidh.resource.infra.ecs_config import ECSConfig
from kobidh.utils.logging import log, log_err, log_warning


class Infra:

    @staticmethod
    def configure(name: str, region: str = None) -> Config:
        config = Config(name, region)
        config.template.set_description(
            "CloudFormation template to manage application infrastructure"
        )

        vpc_config = VPCConfig(config)
        vpc_config._configure()

        iam_config = IAMConfig(config)
        iam_config._configure()

        ecr_config = ECRConfig(config)
        ecr_config._configure()

        ecs_config = ECSConfig(config)
        ecs_config._configure()

        return config

    @staticmethod
    def info(name: str, region: str = None):
        return

    @staticmethod
    def describe(name: str, region: str = None):
        cloud_client = boto3.client("cloudformation", region_name=region)
        stack_name = camelcase(f"{name}-app-stack")
        try:
            # Check if the stack exists
            stacks = cloud_client.describe_stacks(StackName=stack_name)
            log(stacks["Stacks"][0])
            response = cloud_client.get_template(
                StackName=stack_name, TemplateStage="Processed"
            )
            log(response)
        except ClientError as e:
            # If stack does not exist, create it
            if "does not exist" in str(e):
                log(f'App "{name}" does not exist...')
            else:
                log_err(f"Unexpected error: {e}")
                raise

    @staticmethod
    def apply(name: str, region: str, template):
        cloud_client = boto3.client("cloudformation", region_name=region)
        stack_name = camelcase(f"{name}-app-stack")
        response = None
        try:
            # Check if the stack exists
            print(stack_name)
            cloud_client.describe_stacks(StackName=stack_name)
            log(f"Stack {stack_name} exists. Updating it...")

            # Update the existing stack
            response = cloud_client.update_stack(
                StackName=stack_name,
                TemplateBody=template.to_json(),
                Capabilities=["CAPABILITY_NAMED_IAM"],
            )
            log(f"Stack update initiated: {response['StackId']}")

        except ClientError as e:
            # If stack does not exist, create it
            if "does not exist" in str(e):
                log(f"Stack {stack_name} does not exist. Creating it...")
                response = cloud_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template.to_json(),
                    Capabilities=["CAPABILITY_NAMED_IAM"],
                )
                log(f"Stack creation initiated: {response['StackId']}")
            elif "No updates are to be performed" in str(e):
                log_warning(f"No updates are to be performed!")
            else:
                log_err(f"Unexpected error: {e}")
                raise
        return response

    @staticmethod
    def delete(name: str, region: str):
        cloud_client = boto3.client("cloudformation", region_name=region)
        stack_name = camelcase(f"{name}-app-stack")
        response = cloud_client.delete_stack(StackName=stack_name)
        log(response)
        return response
