import boto3
import traceback
from kobidh.utils.format import camelcase
from botocore.exceptions import ClientError
from kobidh.resource.config import Config, StackOutput
from kobidh.resource.infra.vpc_config import VPCConfig
from kobidh.resource.infra.iam_config import IAMConfig
from kobidh.resource.infra.ecr_config import ECRConfig
from kobidh.resource.infra.ecs_config import ECSConfig
from kobidh.utils.logging import log, log_err, log_warning


class Infra:

    @staticmethod
    def _validate_app_stack(name):
        ecs_client = boto3.client("ecs")
        cloudformation_client = boto3.client("cloudformation")
        stack_name = camelcase(f"{name}-infra-stack")
        try:
            response = cloudformation_client.describe_stacks(StackName=stack_name)
            stack = response["Stacks"][0]
            outputs = stack["Outputs"]
            stack_op = StackOutput()
            for op in outputs:
                if op["OutputKey"] == "ClusterName":
                    stack_op.ecs_cluster_name = op["OutputValue"]
                if op["OutputKey"] == "ECRUri":
                    stack_op.ecr_uri = op["OutputValue"]
                if op["OutputKey"] == "PublicSubnetNames":
                    stack_op.public_subnet_names = op["OutputValue"]
                if op["OutputKey"] == "PrivateSubnetNames":
                    stack_op.private_subnet_names = op["OutputValue"]
                if op["OutputKey"] == "ElasticIPAllocationId":
                    stack_op.elastic_ip_allocation_id = op["OutputValue"]
                if op["OutputKey"] == "SecurityGroupName":
                    stack_op.security_group_name = op["OutputValue"]
                if op["OutputKey"] == "InstanceProfileName":
                    stack_op.instance_profile_name = op["OutputValue"]
            if not stack_op.ecs_cluster_name:
                raise Exception(f"Cluster name not found in the stack output.")
            if not stack_op.ecr_uri:
                raise Exception(
                    f"Container Registry URI not found in the stack output."
                )
            # if not stack_op.public_subnet_names:
            #     raise Exception(f"Public Subnet names not found in the stack output.")
            if not stack_op.private_subnet_names:
                raise Exception(f"Private Subnet names not found in the stack output.")
            if not stack_op.elastic_ip_allocation_id:
                raise Exception(
                    f"Elastic IP allocation id not found in the stack output."
                )
            if not stack_op.security_group_name:
                raise Exception(f"Security Group name not found in the stack output.")
            if not stack_op.instance_profile_name:
                raise Exception(f"Instance Profile name not found in the stack output.")
            # Validating the cluster exist
            response = ecs_client.describe_clusters(
                clusters=[stack_op.ecs_cluster_name]
            )
            ecs_cluster = response["clusters"][0]
            return stack_op
        except ClientError as e:
            # If stack does not exist, create it
            if "does not exist" in str(e):
                raise Exception(f'Stack "{stack_name}" does not exist')
            else:
                traceback.print_exc()
                raise Exception(f"Unexpected error: {e}")
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"Unexpected error: {e}")

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
        client = boto3.client("resourcegroupstaggingapi")
        response = client.get_resources(
            TagFilters=[
                {
                    "Key": "environment",
                    "Values": [
                        name,
                    ],
                },
            ],
        )
        for resource in response["ResourceTagMappingList"]:
            log(resource["ResourceARN"])

    @staticmethod
    def describe(name: str, region: str = None):
        cloud_client = boto3.client("cloudformation", region_name=region)
        stack_name = camelcase(f"{name}-infra-stack")
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
    def apply(config: Config):
        cloud_client = boto3.client("cloudformation", region_name=config.region)
        stack_name = camelcase(config.attrs.infra_stack_name)
        response = None
        try:
            # Check if the stack exists
            cloud_client.describe_stacks(StackName=stack_name)
            log(f"Stack {stack_name} exists. Updating it...")

            # Update the existing stack
            response = cloud_client.update_stack(
                StackName=stack_name,
                TemplateBody=config.template.to_json(),
                Capabilities=["CAPABILITY_NAMED_IAM"],
            )
            log(f"Stack update initiated: {response['StackId']}")

        except ClientError as e:
            # If stack does not exist, create it
            if "does not exist" in str(e):
                log(f"Stack {stack_name} does not exist. Creating it...")
                response = cloud_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=config.template.to_json(),
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
        stack_op = Infra._validate_app_stack(name)
        cloud_client = boto3.client("cloudformation", region_name=region)
        stack_name = camelcase(f"{name}-infra-stack")
        response = cloud_client.delete_stack(StackName=stack_name)
        log(response)
        VPCConfig._release_eip(stack_op.elastic_ip_allocation_id)
        return response
