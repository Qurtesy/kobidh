from troposphere import Template
from kobidh.resource.infra.attrs import Attrs


class Config:
    def __init__(self, name: str, region: str = None):
        self.name: str = name
        self.region: str = region
        self.attrs: Attrs = Attrs(name)
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
