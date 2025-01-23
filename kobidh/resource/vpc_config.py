import ipaddress
import boto3
from click import echo
from stringcase import camelcase
from troposphere import Ref
from troposphere.ec2 import (
    InternetGateway,
    VPC,
    Subnet,
    SecurityGroup,
    RouteTable,
    Route,
    SubnetRouteTableAssociation,
    VPCGatewayAttachment,
)
from .config import Config


class VPCConfig:
    """
    Contains VPC configuration details
    """

    def __init__(self, config: Config):
        self.config = config
        self.vpc_name = f"{self.config.name}-vpc"

        self.client = boto3.client("ec2", region_name=self.config.region)

        cidr = ipaddress.IPv4Network("10.10.0.0/16")
        self.cidr = str(cidr)

        self.public_route_table = None

        subnets_list = list(cidr.subnets(new_prefix=22))
        subnets = []
        index = 0
        azones = self._get_azs()
        for az in azones:
            subnets.append(
                {
                    "name": f"{self.config.name}-subnet-{az}",
                    "az": az,
                    "cidr": str(subnets_list[index]),
                    "is_public": True,
                }
            )
            index += 2
        self.subnets_config = subnets
        self.subnets = []

        self.sg_name = f"{self.config.name}-sg"
        self.security_group = None

    def _get_azs(self):
        """
        Fetches the available availability zones for a given AWS region.

        :param region: AWS region name (e.g., 'ap-south-1').
        :return: List of availability zone names.
        """
        try:
            response = self.client.describe_availability_zones(
                Filters=[
                    {"Name": "region-name", "Values": [self.config.region]},
                    {
                        "Name": "state",
                        "Values": ["available"],
                    },  # Only zones that are available
                ]
            )
            zones = [az["ZoneName"] for az in response["AvailabilityZones"]]
            return zones
        except Exception as e:
            echo(f"Error fetching availability zones: {str(e)}")
            return []

    def parse_configuration(self, config: dict):
        """
        Deserialize a JSON string into an VPCConfig object.

        :param json_data: JSON string to deserialize.
        """
        if not config:
            return
        self.vpc_id = config.get("vpc_id", None)
        self.vpc_name = config.get("vpc_name", None)
        self.cidr = config.get("cidr", None)
        self.subnets = config.get("subnets", None)

    def _configure(self):
        vpc_tags = [
            {"Key": "Publisher", "Value": "kobidh"},
            {"Key": "environment", "Value": self.config.name},
            {"Key": "Name", "Value": self.vpc_name},
        ]
        # VPC
        vpc = VPC(
            camelcase(self.vpc_name.replace("-", "_")),
            CidrBlock=self.cidr,
            EnableDnsSupport=True,  # Enable DNS Support
            EnableDnsHostnames=True,  # Enable DNS Hostnames
            InstanceTenancy="default",
            Tags=vpc_tags,
        )
        self.vpc = vpc
        self.config.template.add_resource(vpc)
        self.internet_gateway = InternetGateway(
            camelcase(f"{self.config.name}-ig".replace("-", "_")),
            Tags=[
                {"Key": "Name", "Value": f"{self.config.name}-internet-gateway"},
                {"Key": "environment", "Value": self.config.name},
            ],
        )
        self.config.template.add_resource(self.internet_gateway)
        vpc_gateway_attachment = VPCGatewayAttachment(
            camelcase(f"{self.config.name}-attachment".replace("-", "_")),
            InternetGatewayId=Ref(self.internet_gateway),
            VpcId=Ref(self.vpc),
        )
        self.config.template.add_resource(vpc_gateway_attachment)

        self.public_route_table = RouteTable(
            camelcase(f"{self.config.name}-public".replace("-", "_")),
            VpcId=Ref(self.vpc),
            Tags=[
                {"Key": "Name", "Value": f"{self.config.name}-public"},
                {"Key": "environment", "Value": self.config.name},
            ],
        )
        self.config.template.add_resource(self.public_route_table)

        for subnet in self.subnets_config:
            subnet_tags = [
                {"Key": "Publisher", "Value": "kobidh"},
                {"Key": "environment", "Value": self.config.name},
                {"Key": "Name", "Value": subnet["name"]},
            ]
            # Subnet
            subnet_resource = Subnet(
                camelcase(subnet["name"].replace("-", "_")).replace("_", ""),
                AvailabilityZone=subnet["az"],
                CidrBlock=subnet["cidr"],
                VpcId=Ref(self.vpc),
                MapPublicIpOnLaunch=subnet[
                    "is_public"
                ],  # Map Public IPs for Public Subnets
                Tags=subnet_tags,
            )
            self.config.template.add_resource(subnet_resource)
            self.subnets.append(subnet_resource)
            subnet_route_table_association = SubnetRouteTableAssociation(
                camelcase(
                    f"{self.config.name}-public-subnet-{subnet['az']}".replace("-", "_")
                ).replace("_", ""),
                RouteTableId=Ref(self.public_route_table),
                SubnetId=Ref(subnet_resource),
            )
            self.config.template.add_resource(subnet_route_table_association)

        internet_gateway_route = Route(
            camelcase(f"{self.config.name}-ig-route".format(**locals())),
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=Ref(self.internet_gateway),
            RouteTableId=Ref(self.public_route_table),
        )
        self.config.template.add_resource(internet_gateway_route)

        sg_tags = [
            {"Key": "Publisher", "Value": "kobidh"},
            {"Key": "environment", "Value": self.config.name},
            {"Key": "Name", "Value": self.sg_name},
        ]
        # Security Group to allow all the inbound traffic for ECS
        security_group = SecurityGroup(
            camelcase(self.sg_name.replace("-", "_")),
            GroupName=camelcase(self.sg_name.replace("-", "_")),
            GroupDescription="Allow all inbound traffic for ECS",
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
        self.security_group = security_group
        self.config.template.add_resource(security_group)
