import boto3
from moto import mock_aws
from kobidh.core import Apps
from kobidh.utils.logging import log

REGION = "ap-south-1"


@mock_aws
def test_apps():
    cloud_client = boto3.client("cloudformation", region_name=REGION)
    apps = Apps("tomato", REGION)
    # Test apps.create command
    apps.create()
    # Test apps.delete command
    apps.delete()
