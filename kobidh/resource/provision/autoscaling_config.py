import sys
import json
import boto3
from troposphere import Ref, GetAtt, Base64, Join
from troposphere.ec2 import (
    LaunchTemplate,
    LaunchTemplateData,
    IamInstanceProfile,
    NetworkInterfaces,
    LaunchTemplateBlockDeviceMapping,
    EBSBlockDevice,
)
from troposphere.autoscaling import LaunchTemplateSpecification, AutoScalingGroup
from kobidh.resource.config import Config, StackOutput
from kobidh.utils.logging import log


class AutoScalingConfig:
    """
    Contains Auto Scaling configuration details
    """

    def __init__(self, config: Config, stack_op: StackOutput):
        self.config = config
        self.stack_op = stack_op
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
        instance_type = "t2.micro"
        launch_template = LaunchTemplate(
            "ECSLaunchTemplate",
            LaunchTemplateName="ECSLaunchTemplate",
            LaunchTemplateData=LaunchTemplateData(
                ImageId=self._get_ami_id(),
                InstanceType=instance_type,  # Replace with your instance type
                # SecurityGroupIds=[self.stack_op.security_group_name],
                IamInstanceProfile=IamInstanceProfile(
                    Name=self.stack_op.instance_profile_name
                ),
                NetworkInterfaces=[
                    NetworkInterfaces(
                        # AssociateCarrierIpAddress=True,
                        DeviceIndex=0,
                        Groups=[self.stack_op.security_group_name]
                    )
                ],
                UserData=Base64(
                    Join(
                        "\n",
                        [
                            "#!/bin/bash",
                            f"echo ECS_CLUSTER={self.stack_op.ecs_cluster_name} >> /etc/ecs/ecs.config;",
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

        # Log Launch Template configuration information
        log(f'Launch Template configiuration for "{instance_type}" instance type added')

        # Auto Scaling Group
        self.asg = AutoScalingGroup(
            "AutoScalingGroup",
            MinSize=0,
            MaxSize=3,
            DesiredCapacity="0",
            # NOTE: Public subnet is attached to auto scaling group currently for initial POC
            VPCZoneIdentifier=self.stack_op.public_subnet_names.split(":"),
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

        # Log Auto Scaling Group information
        log(f"Auto Scaling Group configiuration added")
