import boto3
import subprocess
from click import prompt
from kobidh.utils.format import camelcase
from botocore.exceptions import ClientError
from kobidh.resource.config import Config, StackOutput
from kobidh.resource.provision.autoscaling_config import AutoScalingConfig
from kobidh.resource.provision.service_config import ServiceConfig
from kobidh.utils.logging import log, log_err, log_warning


class Provision:

    class Params:
        def __init__(self):
            self.key_pair_name = prompt("Key pair name: ")

    def __init__(self, name: str, region: str = None):
        self.name = name
        self.region = region
        self.config = Config(name, region)
        self.stack_op = StackOutput()
        self.stack_op.validate(name)
        self.params = Provision.Params()

    def configure(self):
        self.config.template.set_description(
            "CloudFormation template to provision application service"
        )
        asg_config = AutoScalingConfig(self.config, self.params, self.stack_op)
        asg_config._configure()
        service_config = ServiceConfig(self.config, self.stack_op)
        service_config._configure()

    def apply(self):
        cloud_client = boto3.client("cloudformation", region_name=self.config.region)
        stack_name = camelcase(f"{self.config.name}-service-stack")
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
                TemplateBody=self.config.template.to_json(),
                Capabilities=["CAPABILITY_NAMED_IAM"],
            )
            log(f"Stack update initiated: {response['StackId']}")

        except ClientError as e:
            # If stack does not exist, create it
            if "does not exist" in str(e):
                log(f"Stack {stack_name} does not exist. Creating it...")
                response = cloud_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=self.config.template.to_json(),
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
    def push(name: str):
        repo_name = f"{name}-repository/web"
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

    @staticmethod
    def release(name: str):
        pass
