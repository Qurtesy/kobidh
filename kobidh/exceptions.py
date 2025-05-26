# kobidh/exceptions.py - Custom exception classes
"""
Custom exception classes for Kobidh application.
Provides specific exceptions for different error scenarios with helpful messages.
"""


class KobidhError(Exception):
    """Base exception class for all Kobidh-related errors"""

    def __init__(self, message: str, suggestion: str = None, error_code: str = None):
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        error_msg = self.message
        if self.error_code:
            error_msg = f"[{self.error_code}] {error_msg}"
        if self.suggestion:
            error_msg += f"\n💡 Suggestion: {self.suggestion}"
        return error_msg


class ConfigurationError(KobidhError):
    """Raised when there's a configuration-related error"""

    def __init__(self, message: str, suggestion: str = None):
        super().__init__(
            message=message,
            suggestion=suggestion
            or "Check your configuration files and environment variables",
            error_code="CONFIG_ERROR",
        )


class AWSError(KobidhError):
    """Base class for AWS-related errors"""

    def __init__(
        self, message: str, aws_error_code: str = None, suggestion: str = None
    ):
        self.aws_error_code = aws_error_code
        super().__init__(
            message=message,
            suggestion=suggestion,
            error_code=f"AWS_{aws_error_code}" if aws_error_code else "AWS_ERROR",
        )


class CredentialsError(AWSError):
    """Raised when there's an issue with AWS credentials"""

    def __init__(self, message: str = "AWS credentials not found or invalid"):
        super().__init__(
            message=message,
            aws_error_code="CREDENTIALS",
            suggestion="Run 'aws configure' or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables",
        )


class RegionError(AWSError):
    """Raised when there's an issue with AWS region"""

    def __init__(self, region: str):
        super().__init__(
            message=f"Invalid or inaccessible AWS region: {region}",
            aws_error_code="REGION",
            suggestion="Check if the region exists and you have access to it",
        )


class ResourceNotFoundError(AWSError):
    """Raised when an AWS resource is not found"""

    def __init__(self, resource_type: str, resource_name: str):
        super().__init__(
            message=f"{resource_type} '{resource_name}' not found",
            aws_error_code="RESOURCE_NOT_FOUND",
            suggestion=f"Verify that the {resource_type.lower()} exists and you have access to it",
        )


class DeploymentError(KobidhError):
    """Raised when deployment operations fail"""

    def __init__(self, message: str, stage: str = None, suggestion: str = None):
        self.stage = stage
        error_code = f"DEPLOY_{stage.upper()}" if stage else "DEPLOY_ERROR"
        super().__init__(
            message=message,
            suggestion=suggestion
            or "Check the CloudFormation console for detailed error information",
            error_code=error_code,
        )


class AppNotFoundError(KobidhError):
    """Raised when an application is not found"""

    def __init__(self, app_name: str):
        super().__init__(
            message=f"Application '{app_name}' not found",
            suggestion="Use 'kobidh apps list' to see available applications",
            error_code="APP_NOT_FOUND",
        )


class AppAlreadyExistsError(KobidhError):
    """Raised when trying to create an app that already exists"""

    def __init__(self, app_name: str):
        super().__init__(
            message=f"Application '{app_name}' already exists",
            suggestion="Use a different name or delete the existing application first",
            error_code="APP_EXISTS",
        )


class ServiceError(KobidhError):
    """Raised when service operations fail"""

    def __init__(self, service_name: str, message: str, suggestion: str = None):
        super().__init__(
            message=f"Service '{service_name}': {message}",
            suggestion=suggestion
            or "Check the ECS console for detailed service information",
            error_code="SERVICE_ERROR",
        )


class ContainerError(KobidhError):
    """Raised when container operations fail"""

    def __init__(self, message: str, suggestion: str = None):
        super().__init__(
            message=message,
            suggestion=suggestion
            or "Check your Dockerfile and container configuration",
            error_code="CONTAINER_ERROR",
        )


class ValidationError(KobidhError):
    """Raised when input validation fails"""

    def __init__(self, field: str, value: str, expected: str):
        super().__init__(
            message=f"Invalid value for {field}: '{value}'",
            suggestion=f"Expected: {expected}",
            error_code="VALIDATION_ERROR",
        )


class NetworkError(AWSError):
    """Raised when there are network-related issues"""

    def __init__(self, message: str, suggestion: str = None):
        super().__init__(
            message=message,
            aws_error_code="NETWORK",
            suggestion=suggestion
            or "Check your VPC configuration and network connectivity",
        )


class CloudFormationError(AWSError):
    """Raised when CloudFormation operations fail"""

    def __init__(self, stack_name: str, message: str, cf_error_code: str = None):
        super().__init__(
            message=f"CloudFormation stack '{stack_name}': {message}",
            aws_error_code=f"CF_{cf_error_code}" if cf_error_code else "CF_ERROR",
            suggestion="Check the CloudFormation console for detailed stack events and error messages",
        )


class PermissionError(AWSError):
    """Raised when there are insufficient permissions"""

    def __init__(self, action: str, resource: str = None):
        message = f"Insufficient permissions to {action}"
        if resource:
            message += f" on {resource}"

        super().__init__(
            message=message,
            aws_error_code="PERMISSION_DENIED",
            suggestion="Check your IAM policies and ensure you have the required permissions",
        )


# Helper functions for exception handling


def handle_boto3_error(func):
    """Decorator to handle common boto3 exceptions and convert them to Kobidh exceptions"""
    from functools import wraps
    from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoCredentialsError:
            raise CredentialsError()
        except NoRegionError:
            raise ConfigurationError(
                "AWS region not specified",
                "Set the AWS_DEFAULT_REGION environment variable or specify region in configuration",
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            # Map common AWS error codes to specific exceptions
            if error_code == "AccessDenied":
                raise PermissionError(f"access resource: {error_message}")
            elif error_code == "ResourceNotFound":
                raise ResourceNotFoundError("Resource", error_message)
            elif error_code == "InvalidParameterException":
                raise ValidationError("parameter", error_message, "valid AWS parameter")
            elif error_code.startswith("InvalidRegion"):
                raise RegionError(kwargs.get("region", "unknown"))
            else:
                # Generic AWS error
                raise AWSError(error_message, error_code)
        except Exception as e:
            # Re-raise Kobidh exceptions as-is
            if isinstance(e, KobidhError):
                raise
            # Wrap other exceptions
            raise KobidhError(f"Unexpected error: {str(e)}")

    return wrapper


def format_error_for_cli(error: KobidhError) -> str:
    """Format error message for CLI display"""
    lines = []

    # Main error message
    lines.append(f"❌ Error: {error.message}")

    # Error code
    if error.error_code:
        lines.append(f"📋 Code: {error.error_code}")

    # Suggestion
    if error.suggestion:
        lines.append(f"💡 Suggestion: {error.suggestion}")

    return "\n".join(lines)


def log_error_details(error: Exception, logger):
    """Log detailed error information for debugging"""
    import traceback

    if isinstance(error, KobidhError):
        logger.error(f"Kobidh Error [{error.error_code}]: {error.message}")
        if error.suggestion:
            logger.info(f"Suggestion: {error.suggestion}")
    else:
        logger.error(f"Unexpected error: {str(error)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")


# Example usage in application code:
"""
from kobidh.exceptions import AppNotFoundError, handle_boto3_error

@handle_boto3_error
def get_app_info(app_name: str):
    # This will automatically handle boto3 exceptions
    cloudformation = boto3.client('cloudformation')
    try:
        response = cloudformation.describe_stacks(StackName=f"{app_name}-stack")
        return response
    except ClientError as e:
        if 'does not exist' in str(e):
            raise AppNotFoundError(app_name)
        raise  # Let the decorator handle other ClientErrors
"""
