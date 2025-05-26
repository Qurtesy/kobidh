import pytest
import boto3
from moto import mock_cloudformation, mock_ecs, mock_ec2


@pytest.fixture
def mock_aws():
    with mock_cloudformation(), mock_ecs(), mock_ec2():
        yield
