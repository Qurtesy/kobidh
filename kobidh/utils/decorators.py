import boto3
import botocore
from click import echo, prompt

def aws_credentails(func):
    def wrapper(*args, **kwargs):
        try:
            session = boto3.Session()
            credentials = session.get_credentials()

            if credentials is None:
                raise Exception("AWS credentials not found. Run `aws configure` to set them up.")
            
            client = session.client("sts")
            identity = client.get_caller_identity()
            echo(f"AWS credentials are set up correctly. Account ID: {identity['Account']}")

        except botocore.exceptions.NoCredentialsError:
            raise Exception("No AWS credentials found. Run `aws configure` to set them up.")
        except botocore.exceptions.PartialCredentialsError:
            raise Exception("Incomplete AWS credentials found. Please check your AWS configuration.")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        return func(*args, **kwargs)
    return wrapper