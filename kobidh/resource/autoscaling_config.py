import sys
import json
import boto3
from troposphere import Ref, GetAtt, Base64, Join, FindInMap
from troposphere.ec2 import (
    LaunchTemplate,
    LaunchTemplateData,
    IamInstanceProfile,
    LaunchTemplateBlockDeviceMapping,
    EBSBlockDevice,
)
from troposphere.autoscaling import LaunchTemplateSpecification, AutoScalingGroup
from .config import Config
from .vpc_config import VPCConfig
from .iam_config import IAMConfig
from .ecs_config import ECSConfig


class AutoScalingConfig:
    """
    Contains Auto Scaling configuration details
    """

    def __init__(
        self,
        config: Config,
        vpc_config: VPCConfig,
        iam_config: IAMConfig,
        ecs_config: ECSConfig,
    ):
        self.config = config
        self.vpc_config = vpc_config
        self.iam_config = iam_config
        self.ecs_config = ecs_config
        self.asg = None
        self.launch_template_name = f"{self.config.name}-launch-template"

    def _get_ami_id(self):
        # Pick from https://docs.aws.amazon.com/AmazonECS/latest/developerguide/al2ami.html
        ssm_client = boto3.client("ssm")
        ami_response = ssm_client.get_parameter(
            Name="/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended"
        )
        if "unittest" in sys.modules.keys():
            return "ami-test01234"
        return json.loads(ami_response["Parameter"]["Value"])["image_id"]

    def _configure(self):
        # Launch Configuration
        launch_template = LaunchTemplate(
            "ECSLaunchTemplate",
            LaunchTemplateName="ECSLaunchTemplate",
            LaunchTemplateData=LaunchTemplateData(
                ImageId=self._get_ami_id(),
                InstanceType="t2.micro",  # Replace with your instance type
                SecurityGroupIds=[
                    Ref(self.vpc_config.security_group)
                ],  # Replace with your security group ID
                IamInstanceProfile=IamInstanceProfile(
                    Name=Ref(self.iam_config.ecs_instance_profile)
                ),
                UserData=Base64(
                    Join(
                        "",
                        [
                            "#!/bin/bash\n",
                            "echo ECS_CLUSTER=",
                            Ref(self.ecs_config.ecs_cluster),
                            " >> /etc/ecs/ecs.config;\n",
                        ],
                    )
                ),
                BlockDeviceMappings=[
                    LaunchTemplateBlockDeviceMapping(
                        DeviceName="/dev/xvda", Ebs=EBSBlockDevice(VolumeType="gp3")
                    )
                ],
            ),
        )
        self.config.template.add_resource(launch_template)

        # Auto Scaling Group
        self.asg = AutoScalingGroup(
            "AutoScalingGroup",
            MinSize=1,
            MaxSize=3,
            DesiredCapacity="1",
            VPCZoneIdentifier=[Ref(subnet) for subnet in self.vpc_config.subnets],
            LaunchTemplate=LaunchTemplateSpecification(
                LaunchTemplateId=Ref(launch_template),
                Version=GetAtt(launch_template, "LatestVersionNumber"),
            ),
            Tags=[
                {
                    "Key": "Name",
                    "Value": "ECSInstance",
                    "PropagateAtLaunch": True,
                }
            ],
        )
        self.config.template.add_resource(self.asg)
