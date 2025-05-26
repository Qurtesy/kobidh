#!/usr/bin/env python3
"""
Project reorganization script for Kobidh
This script helps reorganize the project structure according to the enhancement plan.
"""

import os
import shutil
from pathlib import Path


def reorganize_project():
    """Reorganize the project structure"""

    print("🔄 Starting Kobidh project reorganization...")

    # Get project root
    project_root = Path(__file__).parent.parent
    kobidh_pkg = project_root / "kobidh"

    # Create new directory structure
    new_dirs = [
        "config",
        "templates",
        "scripts",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        "docs/examples",
        "requirements",
        ".github/workflows",
        "kobidh/config",
        "kobidh/commands",
        "kobidh/models",
        "kobidh/services",
        "kobidh/infrastructure",
    ]

    print("📁 Creating new directory structure...")
    for dir_path in new_dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"   Created: {dir_path}")

    # Move and rename existing files
    moves = [
        ("kobidh/resource/infra/vpc_config.py", "kobidh/infrastructure/vpc.py"),
        ("kobidh/resource/infra/ecs_config.py", "kobidh/infrastructure/ecs.py"),
        ("kobidh/resource/infra/ecr_config.py", "kobidh/infrastructure/ecr.py"),
        ("kobidh/resource/infra/iam_config.py", "kobidh/infrastructure/iam.py"),
        (
            "kobidh/resource/infra/__init__.py",
            "kobidh/infrastructure/cloudformation.py",
        ),
        (
            "kobidh/resource/provision/service_config.py",
            "kobidh/services/deployment.py",
        ),
        (
            "kobidh/resource/provision/autoscaling_config.py",
            "kobidh/services/scaling.py",
        ),
        ("kobidh/utils/format.py", "kobidh/utils/formatting.py"),
        ("_requirements/main.txt", "requirements/base.txt"),
        ("_requirements/dev.txt", "requirements/development.txt"),
    ]
    print("📦 Moving and renaming files...")
    for src, dst in moves:
        src_path = project_root / src
        dst_path = project_root / dst

        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            print(f"   Moved: {src} -> {dst}")
        else:
            print(f"   ⚠️  Source not found: {src}")

    # Create __init__.py files
    init_files = [
        "kobidh/config/__init__.py",
        "kobidh/commands/__init__.py",
        "kobidh/models/__init__.py",
        "kobidh/services/__init__.py",
        "kobidh/infrastructure/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
    ]

    print("📄 Creating __init__.py files...")
    for init_file in init_files:
        init_path = project_root / init_file
        if not init_path.exists():
            init_path.write_text("# Auto-generated __init__.py\n")
            print(f"   Created: {init_file}")

    # Clean up empty directories
    cleanup_dirs = ["kobidh/resource", "resource", "service", "meta", "_requirements"]

    print("🧹 Cleaning up empty directories...")
    for cleanup_dir in cleanup_dirs:
        cleanup_path = project_root / cleanup_dir
        if cleanup_path.exists() and cleanup_path.is_dir():
            try:
                contents = list(cleanup_path.iterdir())
                if not contents or all(item.name == "__pycache__" for item in contents):
                    shutil.rmtree(cleanup_path)
                    print(f"   Removed: {cleanup_dir}")
                else:
                    print(f"   ⚠️  Not empty, skipping: {cleanup_dir}")
            except Exception as e:
                print(f"   ⚠️  Could not remove {cleanup_dir}: {e}")
    # Create essential new files
    create_files = {
        "kobidh/constants.py": """# Application constants
VERSION = "1.0.0"
APP_NAME = "kobidh"
CONFIG_DIR = ".kobidh"
DEFAULT_CONFIG_FILE = "config.yaml"
DEFAULT_REGION = "us-east-1"
""",
        "requirements/testing.txt": """-r base.txt
pytest>=6.0.0
pytest-cov>=2.10.0
pytest-mock>=3.6.0
moto>=4.0.0
""",
        "tests/conftest.py": """import pytest
import boto3
from moto import mock_cloudformation, mock_ecs, mock_ec2

@pytest.fixture
def mock_aws():
    with mock_cloudformation(), mock_ecs(), mock_ec2():
        yield
""",
    }

    print("📝 Creating essential new files...")
    for file_path, content in create_files.items():
        full_path = project_root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        print(f"   Created: {file_path}")

    print("✅ Project reorganization completed!")
    print("\n📋 Next steps:")
    print("1. Update import statements in your Python files")
    print(
        "2. Install development dependencies: pip install -r requirements/development.txt"
    )
    print("3. Run tests to ensure everything works: pytest")
    print("4. Review and update the configuration files")


if __name__ == "__main__":
    reorganize_project()
