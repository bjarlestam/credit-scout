import os
import sys
from unittest import mock

# Add the src directory to the path so we can import the project package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Set dummy API keys for testing
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"
os.environ["GEMINI_API_KEY"] = "dummy-key-for-testing"

from credit_scout.main import cli


def test_cli_function_exists():
    """Test that the cli function exists and is callable."""
    assert callable(cli)


def test_package_importable():
    """Test that the credit_scout package can be imported."""
    import credit_scout

    assert credit_scout is not None


@mock.patch("src.credit_scout.main.run_analysis")
@mock.patch("sys.argv", ["credit-scout", "/fake/path/movie.mp4"])
@mock.patch("pathlib.Path.exists", return_value=True)
def test_cli_execution(mock_path_exists, mock_run_analysis):
    """Test that the cli function attempts to run analysis after validating inputs."""
    cli()
    mock_path_exists.assert_called_once()
    mock_run_analysis.assert_called_once_with("/fake/path/movie.mp4")


def test_simple_assertion():
    """A simple test that will always pass."""
    assert True
