import boto3
from moto import mock_aws
from kobidh.service.configuration import Configuration
import logging

logger = logging.getLogger(__name__)

REGION = "ap-south-1"


@mock_aws
def test_apps_create():
    cloud_client = boto3.client("cloudformation", region_name=REGION)
    config = Configuration.configure("fastapi-basicapp", REGION)
    logger.info(config.template.to_json(indent=None))
    response = {"ResponseMetadata": {"HTTPStatusCode": 404}}
    response = cloud_client.create_stack(
        StackName="BasicAppStack", TemplateBody=config.template.to_json()
    )
    logger.info(response)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
