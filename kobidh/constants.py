"""
Application constants for Kobidh deployment automation tool.
"""

# Version information
VERSION = "1.0.0"
APP_NAME = "kobidh"

# Configuration
CONFIG_DIR = ".kobidh"
DEFAULT_CONFIG_FILE = "default.txt"  # Keep compatible with existing code
DEFAULT_REGION = "us-east-1"

# AWS Resource naming patterns
STACK_NAME_PATTERN = "{app}-app-stack"
CLUSTER_NAME_PATTERN = "{app}-cluster"
ECR_REPO_PATTERN = "{app}-repo"

# Default resource configurations
DEFAULT_VPC_CIDR = "10.10.0.0/16"
DEFAULT_INSTANCE_TYPE = "t3.medium"
DEFAULT_MIN_CAPACITY = 1
DEFAULT_MAX_CAPACITY = 10
DEFAULT_DESIRED_CAPACITY = 2

# Timeout settings (in seconds)
CLOUDFORMATION_TIMEOUT = 1800  # 30 minutes
ECS_SERVICE_TIMEOUT = 600  # 10 minutes
ECR_PUSH_TIMEOUT = 1200  # 20 minutes


# Utility functions
def get_stack_name(app_name: str) -> str:
    """Get CloudFormation stack name for app."""
    return STACK_NAME_PATTERN.format(app=app_name)


def get_cluster_name(app_name: str) -> str:
    """Get ECS cluster name for app."""
    return CLUSTER_NAME_PATTERN.format(app=app_name)


def get_ecr_repo_name(app_name: str) -> str:
    """Get ECR repository name for app."""
    return ECR_REPO_PATTERN.format(app=app_name)


# For backward compatibility with existing code
DIR = CONFIG_DIR
DEFAULT_FILE = DEFAULT_CONFIG_FILE
