import boto3
from moto import mock_aws
from kobidh.service.infra import Infra
from kobidh.utils.logging import log

REGION = "ap-south-1"


@mock_aws
def test_apps_create():
    cloud_client = boto3.client("cloudformation", region_name=REGION)
    config = Infra.configure("fastapi-basicapp", REGION)
    log(config.template.to_json(indent=None))
    response = {"ResponseMetadata": {"HTTPStatusCode": 404}}
    response = cloud_client.create_stack(
        StackName="basicAppStack", TemplateBody=config.template.to_json()
    )
    log(response)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
