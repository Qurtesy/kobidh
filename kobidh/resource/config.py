from troposphere import Template


class Config:
    def __init__(self, name: str, region: str = None):
        self.name = name
        self.region = region
        self.template = Template()


class StackOutput:
    def __init__(self):
        self.ecs_cluster_name = None
        self.ecr_uri = None
        self.public_subnet_names = None
        self.private_subnet_names = None
        self.security_group_name = None
        self.instance_profile_name = None
