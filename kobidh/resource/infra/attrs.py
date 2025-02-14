class Attrs:

    def __init__(self, name):
        self.name = name
        # VPC Configuration attribute names
        self.vpc_name = f"{name}-vpc"
        self.internet_gateway_name = f"{name}-ig"
        self.internet_gateway_attachment_name = f"{name}-ig-attachment"
        self.route_table_name = f"{name}-route"
        self.nat_gateway_name = f"{name}-nat"
        self.internet_gateway_route = f"{name}-ig-route"
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
