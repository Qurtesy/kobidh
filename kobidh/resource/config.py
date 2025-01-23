from troposphere import Template


class Config:
    def __init__(self, name: str, region: str = None):
        self.name = name
        self.region = region
        self.template = Template()
        self.template.set_description("CloudFormation template to manage infra")
