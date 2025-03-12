import ipaddress
import boto3
import traceback
from click import prompt
from botocore.exceptions import ClientError
from troposphere import Ref, Join, Output
from troposphere.ec2 import (
    InternetGateway,
    VPC,
    Subnet,
    SecurityGroup,
    RouteTable,
    Route,
    SubnetRouteTableAssociation,
    VPCGatewayAttachment,
    NatGateway,
)
from kobidh.utils.format import camelcase
from kobidh.utils.logging import log, log_err
from kobidh.resource.infra.attrs import Attrs
from kobidh.resource.config import Config


class VPCConfig:
    """
    Contains VPC configuration details
    """

    def __init__(self, config: Config):
        self.config = config

        cidr = ipaddress.IPv4Network("10.10.0.0/16")
        self.cidr = str(cidr)
        self.private_route_table = None
        subnets_list = list(cidr.subnets(new_prefix=22))
        self.subnets_config = []
        index = 0
        azones = self._get_azs()
        azones_count = len(azones)
        for az in azones:
            # Public Subnets configuration
            # self.subnets_config.append(
            #     {
            #         "name": self.config.attrs.public_subnet_name(az),
            #         "az": az,
            #         "cidr": str(subnets_list[index]),
            #         "is_public": True,
            #     }
            # )
            # Private Subnets configuration
            self.subnets_config.append(
                {
                    "name": self.config.attrs.private_subnet_name(az),
                    "az": az,
                    "cidr": str(subnets_list[index + azones_count]),
                    "is_public": False,
                }
            )
            index += 2
        self.public_subnets = []
        self.private_subnets = []

        self.eip_allocation_id = None
        self.security_group = None

    def _get_azs(self):
        """
        Fetches the available availability zones for a given AWS region.

        :param region: AWS region name (e.g., 'ap-south-1').
        :return: List of availability zone names.
        """
        try:
            ec2_client = boto3.client("ec2", region_name=self.config.region)
            response = ec2_client.describe_availability_zones(
                Filters=[
                    {"Name": "region-name", "Values": [self.config.region]},
                    {
                        "Name": "state",
                        "Values": ["available"],
                    },  # Only zones that are available
                ]
            )
            zones = [az["ZoneName"] for az in response["AvailabilityZones"]]
            log(f'Availability Zones for region "{self.config.region}": {zones}')
            return zones
        except Exception as e:
            log_err(f"Error fetching availability zones: {str(e)}")
            return []

    def _allocate_eip(self):
        client = boto3.client("ec2")
        response = client.allocate_address(
            Domain="standard",
            TagSpecifications=[
                {"Tags": [{"Key": "environment", "Value": self.config.name}]}
            ],
        )
        return response["AllocationId"]

    @staticmethod
    def _release_eip(allocation_id):
        client = boto3.client("ec2")
        client.release_address(AllocationId=allocation_id)

    def _configure(self):
        vpc_tags = [
            {"Key": "Publisher", "Value": "kobidh"},
            {"Key": "environment", "Value": self.config.name},
            {"Key": "Name", "Value": self.config.attrs.vpc_name},
        ]
        # VPC
        vpc = VPC(
            camelcase(self.config.attrs.vpc_name),
            CidrBlock=self.cidr,
            EnableDnsSupport=True,  # Enable DNS Support
            EnableDnsHostnames=True,  # Enable DNS Hostnames
            InstanceTenancy="default",
            Tags=vpc_tags,
        )
        self.vpc = vpc
        self.config.template.add_resource(vpc)

        # Log VPC configuration information
        log("VPC configiuration added")
        log(f"CIDR: {self.cidr}")

        self.internet_gateway = InternetGateway(
            camelcase(self.config.attrs.internet_gateway_name),
            Tags=[
                {"Key": "Name", "Value": self.config.attrs.internet_gateway_name},
                {"Key": "environment", "Value": self.config.name},
            ],
        )
        self.config.template.add_resource(self.internet_gateway)
        vpc_gateway_attachment = VPCGatewayAttachment(
            camelcase(self.config.attrs.internet_gateway_attachment_name),
            InternetGatewayId=Ref(self.internet_gateway),
            VpcId=Ref(self.vpc),
        )
        self.config.template.add_resource(vpc_gateway_attachment)

        # Log Internet Gateway configuration information
        log("Internet Gateway configiuration attached to VPC")

        self.private_route_table = RouteTable(
            camelcase(self.config.attrs.route_table_name),
            VpcId=Ref(self.vpc),
            Tags=[
                {"Key": "Name", "Value": self.config.attrs.route_table_name},
                {"Key": "environment", "Value": self.config.name},
            ],
        )
        self.config.template.add_resource(self.private_route_table)
        public_subnet_resource_refs = []
        private_subnet_resource_refs = []
        for subnet in self.subnets_config:
            subnet_tags = [
                {"Key": "Publisher", "Value": "kobidh"},
                {"Key": "environment", "Value": self.config.name},
                {"Key": "Name", "Value": subnet["name"]},
            ]
            # Subnet
            subnet_resource = Subnet(
                camelcase(subnet["name"]),
                AvailabilityZone=subnet["az"],
                CidrBlock=subnet["cidr"],
                VpcId=Ref(self.vpc),
                MapPublicIpOnLaunch=subnet[
                    "is_public"
                ],  # Map Public IPs for Public Subnets
                Tags=subnet_tags,
            )
            self.config.template.add_resource(subnet_resource)
            if subnet["is_public"]:
                self.public_subnets.append(subnet_resource)
            else:
                self.private_subnets.append(subnet_resource)
            subnet_route_table_association = SubnetRouteTableAssociation(
                camelcase(
                    self.config.attrs.public_subnet_route_association_name(subnet["az"])
                    if subnet["is_public"]
                    else self.config.attrs.private_subnet_route_association_name(
                        subnet["az"]
                    )
                ),
                RouteTableId=Ref(self.private_route_table),
                SubnetId=Ref(subnet_resource),
            )
            self.config.template.add_resource(subnet_route_table_association)

            if subnet["is_public"]:
                public_subnet_resource_refs.append(Ref(subnet_resource))
            else:
                private_subnet_resource_refs.append(Ref(subnet_resource))

            # Log Subnet configuration information
            log(f'Subnet "{subnet["name"]}" configuration added and attached to VPC')
        self.config.template.add_output(
            Output(
                "PublicSubnetNames",
                Description="The name of the public Subnets",
                Value=Join(":", public_subnet_resource_refs),
            )
        )
        self.config.template.add_output(
            Output(
                "PrivateSubnetNames",
                Description="The name of the private Subnets",
                Value=Join(":", private_subnet_resource_refs),
            )
        )
        self.eip_allocation_id = self._allocate_eip()
        self.config.template.add_output(
            Output(
                "ElasticIPAllocationId",
                Description=f"The allocation id of Elastic IP",
                Value=self.eip_allocation_id,
            )
        )
        self.nat_gateway = NatGateway(
            camelcase(self.config.attrs.nat_gateway_name),
            AllocationId=self.eip_allocation_id,
            SubnetId=Ref(self.private_subnets[0]),
            Tags=[
                {"Key": "Name", "Value": self.config.attrs.nat_gateway_name},
                {"Key": "environment", "Value": self.config.name},
            ],
        )
        self.config.template.add_resource(self.nat_gateway)

        nat_gateway_route = Route(
            camelcase(self.config.attrs.nat_route_name),
            DestinationCidrBlock="0.0.0.0/0",
            NatGatewayId=Ref(self.nat_gateway),
            RouteTableId=Ref(self.private_route_table),
        )
        self.config.template.add_resource(nat_gateway_route)

        # Log NAT Gateway configuration information
        log("NAT Gateway configiuration attached to Route Table")

        sg_tags = [
            {"Key": "Publisher", "Value": "kobidh"},
            {"Key": "environment", "Value": self.config.name},
            {"Key": "Name", "Value": self.config.attrs.security_group_name},
        ]
        # Security Group to allow all the inbound traffic for ECS
        security_group_description = "Allow all inbound traffic for ECS"
        self.security_group = SecurityGroup(
            camelcase(self.config.attrs.security_group_name),
            GroupName=camelcase(self.config.attrs.security_group_name),
            GroupDescription=security_group_description,
            SecurityGroupIngress=[
                # Allow SSH
                {
                    "IpProtocol": "TCP",
                    "FromPort": 22,
                    "ToPort": 22,
                    "CidrIp": "0.0.0.0/0",
                },
                # Allow HTTP
                # {
                #     "IpProtocol": "TCP",
                #     "FromPort": 80,
                #     "ToPort": 80,
                #     "CidrIp": "0.0.0.0/0"
                # },
                # Allow HTTPS
                # {
                #     "IpProtocol": "TCP",
                #     "FromPort": 443,
                #     "ToPort": 443,
                #     "CidrIp": "0.0.0.0/0"
                # },
            ],
            VpcId=Ref(self.vpc),
            Tags=sg_tags,
        )
        self.config.template.add_resource(self.security_group)
        self.config.template.add_output(
            Output(
                "SecurityGroupName",
                Description=f'The Security Group name of "{security_group_description}"',
                Value=Ref(self.security_group),
            )
        )

        # Log Security Group configuration information
        log(f'Security Group "{security_group_description}" configiuration added')
