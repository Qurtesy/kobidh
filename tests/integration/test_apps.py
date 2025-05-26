"""
Test for Apps functionality using moto for AWS mocking
"""

import boto3
import pytest
from moto import mock_aws
from kobidh.core import Apps
from kobidh.utils.logging import log

REGION = "ap-south-1"


@pytest.fixture
def mock_aws_environment():
    """Set up mocked AWS environment for testing"""
    with mock_aws():
        yield


@pytest.mark.integration
def test_apps_create_and_delete(mock_aws_environment):
    """Test creating and deleting an application"""
    cloud_client = boto3.client("cloudformation", region_name=REGION)
    apps = Apps("tomato", REGION)

    # Test apps.create command
    apps.create()

    # Test apps.delete command
    apps.delete()


@pytest.mark.integration
def test_apps_describe(mock_aws_environment):
    """Test describing an application"""
    apps = Apps("test-app", REGION)

    # This should not raise an exception for non-existent app
    # The actual behavior will depend on implementation
    apps.describe()


@pytest.mark.integration
def test_apps_info(mock_aws_environment):
    """Test getting application info"""
    apps = Apps("test-app", REGION)

    # This should not raise an exception for non-existent app
    # The actual behavior will depend on implementation
    apps.info()
