import boto3
import traceback
from troposphere import Template
from kobidh.utils.format import camelcase
from botocore.exceptions import ClientError
from kobidh.utils.logging import log, log_err, log_warning
from kobidh.resource.infra.attrs import Attrs


class Config:

    class Attrs:

        def __init__(self, name: str):
            self.name = name
            self.infra_stack_name = f"{name}-infra-stack"
            self.provision_stack_name = f"{name}-provision-stack"
            # VPC Configuration attribute names
            self.vpc_name = f"{name}-vpc"
            self.internet_gateway_name = f"{name}-ig"
            self.internet_gateway_attachment_name = f"{name}-ig-attachment"
            self.route_table_name = f"{name}-route"
            self.nat_gateway_name = f"{name}-nat"
            self.internet_gateway_route = f"{name}-ig-route"
            self.nat_route_name = f"{name}-nat-route"
            self.security_group_name = f"{name}-sg"
            # IAM Configuration attribute names
            self.ecs_policy_name = f"{name}-ecs-policy"
            self.ecs_tag_resource_policy_name = f"{name}-ecs-tag-resource-policy"
            self.ecs_role_name = f"{name}-instance-role"
            self.ecs_profile_name = f"{name}-instance-profile"
            # ECS Configuration attribute name(s)
            self.cluster_name = f"{name}-cluster"
            # ECR Configuration attribute name(s)
            self.ecr_name = f"{name}-repository"

        def public_subnet_name(self, az):
            return f"{self.name}-{az}-public-subnet"

        def private_subnet_name(self, az):
            return f"{self.name}-{az}-private-subnet"

        def public_subnet_route_association_name(self, az):
            return f"{self.name}-{az}-public-subnet-assoc"

        def private_subnet_route_association_name(self, az):
            return f"{self.name}-{az}-private-subnet-assoc"

    def __init__(self, name: str, region: str = None):
        self.name: str = name
        self.region: str = region
        self.attrs: Config.Attrs = Config.Attrs(name)
        self.template: Template = Template()


class StackOutput:
    def __init__(self):
        self.ecs_cluster_name: str = None
        self.ecr_uri: str = None
        self.public_subnet_names: str = None
        self.private_subnet_names: str = None
        self.elastic_ip_allocation_id: str = None
        self.security_group_name: str = None
        self.instance_profile_name: str = None

    def validate(self, name):
        ecs_client = boto3.client("ecs")
        cloudformation_client = boto3.client("cloudformation")
        stack_name = camelcase(f"{name}-app-stack")
        try:
            response = cloudformation_client.describe_stacks(StackName=stack_name)
            assert (
                "Stacks" in response
            ), f'"Stack" key not found in the Cloudformation stack "{stack_name}"'
            assert (
                len(response["Stacks"]) > 0
            ), f'Stack not found in the Cloudformation stack "{stack_name}"'
            stack = response["Stacks"][0]
            assert (
                "Outputs" in stack
            ), f'"Outputs" key not found in the Cloudformation stack "{stack_name}",\
                  please wait for sometime after creating an app and try again'
            outputs = stack["Outputs"]
            for op in outputs:
                if op["OutputKey"] == "ClusterName":
                    self.ecs_cluster_name = op["OutputValue"]
                if op["OutputKey"] == "ECRUri":
                    self.ecr_uri = op["OutputValue"]
                if op["OutputKey"] == "PublicSubnetNames":
                    self.public_subnet_names = op["OutputValue"]
                if op["OutputKey"] == "PrivateSubnetNames":
                    self.private_subnet_names = op["OutputValue"]
                if op["OutputKey"] == "SecurityGroupName":
                    self.security_group_name = op["OutputValue"]
                if op["OutputKey"] == "InstanceProfileName":
                    self.instance_profile_name = op["OutputValue"]
            if not self.ecs_cluster_name:
                log_err(f"Cluster name not found in the stack output.")
            if not self.ecr_uri:
                log_err(f"Container Registry URI not found in the stack output.")
            if not self.public_subnet_names:
                log_err(f"Public Subnet names not found in the stack output.")
            if not self.security_group_name:
                log_err(f"Security Group name not found in the stack output.")
            if not self.instance_profile_name:
                log_err(f"Instance Profile name not found in the stack output.")
            # Validating the cluster exist
            response = ecs_client.describe_clusters(clusters=[self.ecs_cluster_name])
            assert (
                len(response["clusters"]) > 0
            ), f'Cluster with name "{self.ecs_cluster_name}" not found'
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
