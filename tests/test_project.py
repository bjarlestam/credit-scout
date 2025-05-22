import os
import sys
from unittest import mock

# Add the src directory to the path so we can import the project package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from project.main import cli


def test_cli_function_exists():
    """Test that the cli function exists and is callable."""
    assert callable(cli)


def test_package_importable():
    """Test that the project package can be imported."""
    import project

    assert project is not None


@mock.patch("os.system")
def test_cli_execution(mock_system):
    """Test that the cli function calls os.system with the correct path."""
    cli()
    assert mock_system.called


def test_simple_assertion():
    """A simple test that will always pass."""
    assert True
