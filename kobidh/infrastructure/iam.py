from kobidh.utils.format import camelcase
from troposphere import Ref, Output
from troposphere.iam import Role, Policy, InstanceProfile
from kobidh.resource.config import Config


class IAMConfig:
    """
    Contains VPC configuration details
    """

    def __init__(self, config: Config):
        self.config = config
        self.ecs_instance_profile = None

    def _configure(self):
        # IAM Role for ECS EC2 Instances
        ecs_instance_role = Role(
            camelcase(self.config.attrs.ecs_role_name),
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
                    PolicyName=camelcase(self.config.attrs.ecs_policy_name),
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
                        self.config.attrs.ecs_tag_resource_policy_name
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
            camelcase(self.config.attrs.ecs_profile_name),
            Roles=[Ref(ecs_instance_role)],
        )
        self.config.template.add_resource(self.ecs_instance_profile)
        self.config.template.add_output(
            Output(
                "InstanceProfileName",
                Description=f"The instance Profile name",
                Value=Ref(self.ecs_instance_profile),
            )
        )
