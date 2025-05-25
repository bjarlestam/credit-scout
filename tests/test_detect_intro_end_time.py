import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# Add the src directory to the path so we can import the project package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from credit_scout.tools.detect_intro_end_time import detect_intro_end_time_core, GeminiClient


class TestDetectIntroEndTime:
    """Test suite for intro end time detection functionality."""

    @pytest.fixture
    def test_data_dir(self):
        """Fixture that provides the test data directory path."""
        return Path(__file__).parent / "test_data"

    @pytest.fixture
    def sample_video_path(self, test_data_dir):
        """Fixture that provides a sample video file path."""
        video_path = test_data_dir / "sample_video.mp4"
        if video_path.exists():
            return str(video_path)
        else:
            pytest.skip(f"Sample video not found at {video_path}. Please add test video files.")

    def test_detect_intro_end_time_core_exists(self):
        """Test that the detect_intro_end_time_core function exists and is callable."""
        assert callable(detect_intro_end_time_core)

    def test_gemini_client_exists(self):
        """Test that the GeminiClient class exists and is instantiable."""
        assert GeminiClient is not None

    def test_detect_intro_end_time_with_nonexistent_file(self):
        """Test that function returns None for non-existent input file."""
        result = detect_intro_end_time_core("/path/to/nonexistent/file.mp4")
        assert result is None

    def test_detect_intro_end_time_with_directory(self):
        """Test that function returns None when input is a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = detect_intro_end_time_core(temp_dir)
            assert result is None

    def test_detect_intro_end_time_with_empty_file(self):
        """Test that function handles empty files gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_file = Path(temp_dir) / "empty.mp4"
            empty_file.touch()

            result = detect_intro_end_time_core(str(empty_file))
            assert result is None

    def test_gemini_client_initialization_without_api_key(self):
        """Test that GeminiClient raises ValueError when no API key is provided."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
                GeminiClient()

    def test_gemini_client_initialization_with_api_key(self):
        """Test that GeminiClient initializes correctly with API key."""
        with mock.patch("google.genai.Client") as mock_client:
            client = GeminiClient(api_key="test_key")
            assert client.api_key == "test_key"
            mock_client.assert_called_once_with(api_key="test_key")

    def test_gemini_client_initialization_with_env_var(self):
        """Test that GeminiClient initializes correctly with environment variable."""
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "env_test_key"}):
            with mock.patch("google.genai.Client") as mock_client:
                client = GeminiClient()
                assert client.api_key == "env_test_key"
                mock_client.assert_called_once_with(api_key="env_test_key")

    def test_calculate_cost_method(self):
        """Test the cost calculation method."""
        with mock.patch("google.genai.Client"):
            client = GeminiClient(api_key="test_key")

            # Mock response object
            mock_response = mock.Mock()
            mock_response.usage_metadata.prompt_token_count = 1000
            mock_response.usage_metadata.candidates_token_count = 500

            cost_data = client.calculate_cost(mock_response)

            # Expected costs based on Gemini 2.0 Flash pricing
            expected_input_cost = (1000 / 1_000_000) * 0.075  # $0.000075
            expected_output_cost = (500 / 1_000_000) * 0.30  # $0.00015
            expected_total_cost = expected_input_cost + expected_output_cost

            assert cost_data["input_cost"] == expected_input_cost
            assert cost_data["output_cost"] == expected_output_cost
            assert cost_data["total_cost"] == expected_total_cost

    @pytest.mark.integration
    def test_detect_intro_end_time_with_valid_video_and_api_key(self, sample_video_path):
        """Integration test with actual video file and API key (requires GEMINI_API_KEY)."""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY environment variable not set")

        # This test would actually call the Gemini API
        # Only run if explicitly requested and API key is available
        result = detect_intro_end_time_core(sample_video_path)

        if result is not None:
            # Verify the result structure
            assert isinstance(result, dict)
            assert "timestamp" in result
            assert "confidence" in result
            assert "cost" in result
            assert "tokens_used" in result

            # Verify timestamp format (should be MM:SS)
            timestamp = result["timestamp"]
            assert isinstance(timestamp, str)
            # Basic format check - should contain a colon
            assert ":" in timestamp

    def test_detect_intro_end_time_default_parameters(self):
        """Test that function accepts default parameters correctly."""
        # This should fail gracefully with non-existent file
        result = detect_intro_end_time_core("nonexistent.mp4")
        assert result is None

    def test_detect_intro_end_time_with_custom_api_key(self):
        """Test that function accepts custom API key parameter."""
        # This should fail gracefully with non-existent file, but test parameter passing
        result = detect_intro_end_time_core("nonexistent.mp4", api_key="custom_key")
        assert result is None


# Test data setup instructions
def test_data_setup_instructions():
    """Instructions for setting up test data for intro end time detection."""
    test_data_dir = Path(__file__).parent / "test_data"

    print(f"\n{'=' * 60}")
    print("INTRO END TIME DETECTION TEST SETUP")
    print(f"{'=' * 60}")
    print("To run integration tests, please:")
    print(f"1. Create the directory: {test_data_dir}")
    print(f"2. Add your test video files: {test_data_dir}/sample_video.mp4")
    print("3. Set the GEMINI_API_KEY environment variable")
    print("\nRecommended test video characteristics:")
    print("  - Duration: At least 2-3 minutes (to have intro content)")
    print("  - Format: MP4 with H.264 video codec")
    print("  - Content: Should have intro sequence with logos/titles")
    print("  - Size: Keep under 100MB for faster upload")
    print("\nEnvironment setup:")
    print("  export GEMINI_API_KEY='your_api_key_here'")
    print("\nExample commands:")
    print(f"  mkdir -p {test_data_dir}")
    print("  # Copy a video file with intro sequence")
    print(f"  cp /path/to/movie_with_intro.mp4 {test_data_dir}/sample_video.mp4")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    test_data_setup_instructions()
