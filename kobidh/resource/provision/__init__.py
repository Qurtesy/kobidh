import boto3
import traceback
import subprocess
from kobidh.utils.format import camelcase
from botocore.exceptions import ClientError
from kobidh.resource.config import Config, StackOutput
from kobidh.resource.provision.autoscaling_config import AutoScalingConfig
from kobidh.resource.provision.service_config import ServiceConfig
from kobidh.utils.logging import log, log_err, log_warning


class Provision:
    @staticmethod
    def _validate_cloudformation_stack(name):
        ecs_client = boto3.client("ecs")
        cloudformation_client = boto3.client("cloudformation")
        stack_name = camelcase(f"{name}-app-stack")
        try:
            response = cloudformation_client.describe_stacks(StackName=stack_name)
            assert "Stacks" in response, f"\"Stack\" key not found in the Cloudformation stack \"{stack_name}\""
            assert len(response["Stacks"]) > 0, f"Stack not found in the Cloudformation stack \"{stack_name}\""
            stack = response["Stacks"][0]
            assert "Outputs" in stack, f"\"Outputs\" key not found in the Cloudformation stack \"{stack_name}\",\
                  please wait for sometime after creating an app and try again"
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
                if op["OutputKey"] == "SecurityGroupName":
                    stack_op.security_group_name = op["OutputValue"]
                if op["OutputKey"] == "InstanceProfileName":
                    stack_op.instance_profile_name = op["OutputValue"]
            if not stack_op.ecs_cluster_name:
                log_err(f"Cluster name not found in the stack output.")
            if not stack_op.ecr_uri:
                log_err(f"Container Registry URI not found in the stack output.")
            if not stack_op.public_subnet_names:
                log_err(f"Public Subnet names not found in the stack output.")
            if not stack_op.security_group_name:
                log_err(f"Security Group name not found in the stack output.")
            if not stack_op.instance_profile_name:
                log_err(f"Instance Profile name not found in the stack output.")
            # Validating the cluster exist
            response = ecs_client.describe_clusters(
                clusters=[stack_op.ecs_cluster_name]
            )
            ecs_cluster = response["clusters"][0]
            return stack_op
        except AssertionError as e:
            log_err(f"Assertion error: {e}")
            raise e
        except ClientError as e:
            # If stack does not exist, create it
            if "does not exist" in str(e):
                log_err(f'Stack "{stack_name}" does not exist')
            else:
                traceback.print_exc()
                log_err(f"Unexpected error: {e}")
            raise e
        except Exception as e:
            traceback.print_exc()
            log_err(f"Unexpected error: {e}")
            raise e

    @staticmethod
    def configure(name: str, region: str = None):
        stack_op = Provision._validate_cloudformation_stack(name)

        config = Config(name, region)
        config.template.set_description(
            "CloudFormation template to provision application service"
        )

        asg_config = AutoScalingConfig(config, stack_op)
        asg_config._configure()

        service_config = ServiceConfig(config, stack_op)
        service_config._configure()

        return config

    @staticmethod
    def apply(config: Config):
        cloud_client = boto3.client("cloudformation", region_name=config.region)
        stack_name = camelcase(f"{config.name}-service-stack")
        response = None
        try:
            # Check if the stack exists
            response = cloud_client.describe_stacks(StackName=stack_name)
            log(f"Stack {stack_name} exists.")
            stack_status = response["Stacks"][0]["StackStatus"]
            if stack_status == "ROLLBACK_COMPLETE":
                log_warning(
                    f"Stack is in ROLLBACK_COMPLETE state!\nStack can not be updated in this state."
                )
                return response
            log(f"Stack status: {stack_status}")
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
            elif "in ROLLBACK_COMPLETE state and can not be updated" in str(e):
                log_warning(
                    f"Stack is in ROLLBACK_COMPLETE state!\nStack can not be updated in this state."
                )
            else:
                log_err(f"Unexpected error: {e}")
                raise
        return response

    @staticmethod
    def delete(name: str, region: str):
        cloud_client = boto3.client("cloudformation", region_name=region)
        stack_name = camelcase(f"{name}-service-stack")
        response = cloud_client.delete_stack(StackName=stack_name)
        log(response)
        return response

    @staticmethod
    def push(name: str, region: str):
        repo_name = "tomato-repository/web"
        tag = "1.0.2"
        # Build docker image and tag it to the repository name
        subprocess.run(["docker", "build", "-t", repo_name, "."])
        # Build docker image and tag it to the ECR repository name and version
        subprocess.run(
            [
                "docker",
                "tag",
                f"{repo_name}:latest",
                f"295920452208.dkr.ecr.ap-south-1.amazonaws.com/{repo_name}:{tag}",
            ]
        )
        # Build docker image and tag it to the ECR repository name and latest
        subprocess.run(
            [
                "docker",
                "tag",
                f"{repo_name}:latest",
                f"295920452208.dkr.ecr.ap-south-1.amazonaws.com/{repo_name}:latest",
            ]
        )
        # Push the docker image(s) to ECR
        subprocess.run(
            [
                "docker",
                "push",
                f"295920452208.dkr.ecr.ap-south-1.amazonaws.com/{repo_name}",
            ]
        )
