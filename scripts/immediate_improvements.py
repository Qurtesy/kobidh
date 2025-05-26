#!/usr/bin/env python3
"""
Immediate improvements script for Kobidh
This script implements critical improvements without major restructuring.
"""

import os
from pathlib import Path


def create_immediate_improvements():
    """Create immediate improvements to the current codebase"""

    print("🚀 Implementing immediate improvements for Kobidh...")

    project_root = Path(__file__).parent.parent

    # 1. Create enhanced exceptions
    exceptions_content = '''"""Custom exception classes for better error handling"""

class KobidhError(Exception):
    """Base exception for all Kobidh errors"""
    def __init__(self, message: str, suggestion: str = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def __str__(self):
        result = self.message
        if self.suggestion:
            result += f"\\n💡 Suggestion: {self.suggestion}"
        return result

class ConfigurationError(KobidhError):
    """Configuration-related errors"""
    pass

class AWSError(KobidhError):
    """AWS-related errors"""
    pass

class DeploymentError(KobidhError):  
    """Deployment-related errors"""
    pass
'''

    exceptions_path = project_root / "kobidh" / "exceptions.py"
    exceptions_path.write_text(exceptions_content)
    print("✅ Created enhanced exception handling")
    # 2. Create constants file
    constants_content = '''"""Application constants"""

VERSION = "1.0.0"
APP_NAME = "kobidh"
CONFIG_DIR = ".kobidh"
DEFAULT_CONFIG_FILE = "default.txt"
DEFAULT_REGION = "us-east-1"

# AWS Resource naming
def get_stack_name(app_name: str) -> str:
    """Get CloudFormation stack name for app"""
    return f"{app_name}-app-stack"

def get_cluster_name(app_name: str) -> str:
    """Get ECS cluster name for app"""
    return f"{app_name}-cluster"
'''

    constants_path = project_root / "kobidh" / "constants.py"
    constants_path.write_text(constants_content)
    print("✅ Created constants file")

    # 3. Enhanced requirements
    req_base = """click==8.1.8
stringcase==1.2.0
troposphere==4.8.3
boto3==1.36.4
setuptools
pyyaml>=6.0
"""

    req_dev = """-r main.txt
pytest>=6.0.0
pytest-cov>=2.10.0
pytest-mock>=3.6.0
moto>=4.0.0
black>=22.0.0
flake8>=4.0.0
"""

    req_path = project_root / "_requirements"
    (req_path / "main.txt").write_text(req_base)
    (req_path / "dev.txt").write_text(req_dev)
    print("✅ Updated requirements files")

    print("✅ Immediate improvements completed!")


if __name__ == "__main__":
    create_immediate_improvements()
