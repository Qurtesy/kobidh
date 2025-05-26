"""
Basic unit tests for Kobidh core functionality.
"""

from kobidh.exceptions import KobidhError, ConfigurationError
from kobidh.constants import VERSION, APP_NAME, CONFIG_DIR


def test_version():
    """Test version constant exists."""
    assert VERSION == "1.0.0"


def test_app_name():
    """Test app name constant."""
    assert APP_NAME == "kobidh"


def test_custom_exception():
    """Test custom exception works."""
    error = KobidhError("Test error", "Test suggestion")
    assert "Test error" in str(error)
    assert "Test suggestion" in str(error)


def test_configuration_error():
    """Test ConfigurationError inherits from KobidhError."""
    error = ConfigurationError("Config error")
    assert isinstance(error, KobidhError)


def test_core_imports():
    """Test that core modules can be imported."""
    from kobidh import core

    assert hasattr(core, "Core")
    assert hasattr(core, "Apps")


def test_cli_imports():
    """Test that CLI module imports."""
    from kobidh import cli

    assert hasattr(cli, "main")


def test_apps_validation():
    """Test Apps class validation."""
    from kobidh.core import Apps

    # Test invalid name
    try:
        Apps("")
        assert False, "Should have raised ConfigurationError"
    except ConfigurationError as e:
        assert "Application name cannot be empty" in str(e)


if __name__ == "__main__":
    # Run tests manually
    test_version()
    test_app_name()
    test_custom_exception()
    test_configuration_error()
    test_core_imports()
    test_cli_imports()
    test_apps_validation()
    print("✅ All tests passed!")
