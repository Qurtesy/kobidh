from stringcase import camelcase
from troposphere import Ref
from troposphere.iam import Role, Policy, InstanceProfile
from .config import Config


class IAMConfig:
    """
    Contains VPC configuration details
    """

    def __init__(self, config: Config):
        self.config = config
        self.ecs_policy_name = f"{self.config.name}-ecs-policy"
        self.ecs_tag_resource_policy_name = (
            f"{self.config.name}-ecs-tag-resource-policy"
        )
        self.ecs_role_name = f"{self.config.name}-instance-role"
        self.ecs_profile_name = f"{self.config.name}-instance-profile"
        self.ecs_instance_profile = None

    def _configure(self):
        # IAM Role for ECS EC2 Instances
        ecs_instance_role = Role(
            camelcase(self.ecs_role_name.replace("-", "_")),
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            },
            Policies=[
                Policy(
                    PolicyName=camelcase(self.ecs_policy_name.replace("-", "_")),
                    PolicyDocument={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "ecs:CreateCluster",
                                    "ecs:DeregisterContainerInstance",
                                    "ecs:DiscoverPollEndpoint",
                                    "ecs:Poll",
                                    "ecs:RegisterContainerInstance",
                                    "ecs:StartTelemetrySession",
                                    "ecs:UpdateContainerInstancesState",
                                    "ecs:Submit*",
                                    "ecr:GetAuthorizationToken",
                                    "ecr:BatchCheckLayerAvailability",
                                    "ecr:GetDownloadUrlForLayer",
                                    "ecr:BatchGetImage",
                                    "ec2:Describe*",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents",
                                ],
                                "Resource": "*",
                            }
                        ],
                    },
                ),
                Policy(
                    PolicyName=camelcase(
                        self.ecs_tag_resource_policy_name.replace("-", "_")
                    ),
                    PolicyDocument={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "ecs:TagResource",
                                "Resource": "*",
                                "Condition": {
                                    "StringEquals": {
                                        "ecs:CreateAction": [
                                            "CreateCluster",
                                            "RegisterContainerInstance",
                                        ]
                                    }
                                },
                            }
                        ],
                    },
                ),
            ],
        )
        self.config.template.add_resource(ecs_instance_role)

        # IAM Instance Profile
        self.ecs_instance_profile = InstanceProfile(
            camelcase(self.ecs_profile_name.replace("-", "_")),
            Roles=[Ref(ecs_instance_role)],
        )
        self.config.template.add_resource(self.ecs_instance_profile)
