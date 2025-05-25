import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# Add the src directory to the path so we can import the project package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from credit_scout.tools.encode_intro_segment import encode_intro_segment_core
from credit_scout.tools.encode_outro_segment import encode_outro_segment_core


class TestVideoEncoding:
    """Test suite for video encoding functions."""

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

    @pytest.fixture
    def temp_dir(self):
        """Fixture that provides a temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp(prefix="test_credit_scout_")
        yield temp_dir
        # Cleanup after test
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestIntroSegmentEncoding(TestVideoEncoding):
    """Tests for intro segment encoding functionality."""

    def test_encode_intro_segment_core_exists(self):
        """Test that the encode_intro_segment_core function exists and is callable."""
        assert callable(encode_intro_segment_core)

    def test_encode_intro_segment_with_nonexistent_file(self):
        """Test that function returns None for non-existent input file."""
        result = encode_intro_segment_core("/path/to/nonexistent/file.mp4")
        assert result is None

    def test_encode_intro_segment_with_directory(self, temp_dir):
        """Test that function returns None when input is a directory."""
        result = encode_intro_segment_core(temp_dir)
        assert result is None

    def test_encode_intro_segment_with_empty_file(self, temp_dir):
        """Test that function handles empty files gracefully."""
        empty_file = Path(temp_dir) / "empty.mp4"
        empty_file.touch()

        result = encode_intro_segment_core(str(empty_file))
        assert result is None

    @pytest.mark.integration
    def test_encode_intro_segment_with_valid_video(self, sample_video_path):
        """Integration test with actual video file."""
        result = encode_intro_segment_core(
            video_file_path=sample_video_path,
            duration=5.0,  # Short duration for testing
            video_height=240,  # Lower resolution for faster processing
            video_fps=10,  # Lower FPS for faster processing
        )

        if result is not None:
            # Verify output file exists and has content
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
            assert result.endswith(".mp4")
            assert "intro_segment_" in os.path.basename(result)

            # Cleanup
            try:
                temp_dir = os.path.dirname(result)
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def test_encode_intro_segment_default_parameters(self):
        """Test that function accepts default parameters correctly."""
        # This should fail gracefully with non-existent file
        result = encode_intro_segment_core("nonexistent.mp4")
        assert result is None

    def test_encode_intro_segment_custom_parameters(self):
        """Test that function accepts custom parameters correctly."""
        result = encode_intro_segment_core(
            video_file_path="nonexistent.mp4", duration=120.0, video_height=480, video_crf=20, video_fps=24
        )
        assert result is None  # Should fail due to non-existent file

    @mock.patch("subprocess.run")
    def test_encode_intro_segment_ffmpeg_failure(self, mock_subprocess, sample_video_path):
        """Test handling of ffmpeg execution failure."""
        if sample_video_path is None:
            pytest.skip("No sample video available")

        # Mock subprocess to raise CalledProcessError
        from subprocess import CalledProcessError

        mock_subprocess.side_effect = CalledProcessError(1, "ffmpeg", stderr="Mock error")

        result = encode_intro_segment_core(sample_video_path)
        assert result is None

    @mock.patch("subprocess.run")
    def test_encode_intro_segment_ffmpeg_not_found(self, mock_subprocess, sample_video_path):
        """Test handling when ffmpeg is not installed."""
        if sample_video_path is None:
            pytest.skip("No sample video available")

        # Mock subprocess to raise FileNotFoundError
        mock_subprocess.side_effect = FileNotFoundError("ffmpeg not found")

        result = encode_intro_segment_core(sample_video_path)
        assert result is None


class TestOutroSegmentEncoding(TestVideoEncoding):
    """Tests for outro segment encoding functionality."""

    def test_encode_outro_segment_core_exists(self):
        """Test that the encode_outro_segment_core function exists and is callable."""
        assert callable(encode_outro_segment_core)

    def test_encode_outro_segment_with_nonexistent_file(self):
        """Test that function returns None for non-existent input file."""
        result = encode_outro_segment_core("/path/to/nonexistent/file.mp4")
        assert result is None

    def test_encode_outro_segment_with_directory(self, temp_dir):
        """Test that function returns None when input is a directory."""
        result = encode_outro_segment_core(temp_dir)
        assert result is None

    def test_encode_outro_segment_with_empty_file(self, temp_dir):
        """Test that function handles empty files gracefully."""
        empty_file = Path(temp_dir) / "empty.mp4"
        empty_file.touch()

        result = encode_outro_segment_core(str(empty_file))
        assert result is None

    @pytest.mark.integration
    def test_encode_outro_segment_with_valid_video(self, sample_video_path):
        """Integration test with actual video file."""
        result = encode_outro_segment_core(
            video_file_path=sample_video_path,
            duration=5.0,  # Short duration for testing
            video_height=240,  # Lower resolution for faster processing
            video_fps=10,  # Lower FPS for faster processing
        )

        if result is not None:
            # Verify output file exists and has content
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
            assert result.endswith(".mp4")
            assert "outro_segment_" in os.path.basename(result)

            # Cleanup
            try:
                temp_dir = os.path.dirname(result)
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def test_encode_outro_segment_default_parameters(self):
        """Test that function accepts default parameters correctly."""
        # This should fail gracefully with non-existent file
        result = encode_outro_segment_core("nonexistent.mp4")
        assert result is None

    def test_encode_outro_segment_custom_parameters(self):
        """Test that function accepts custom parameters correctly."""
        result = encode_outro_segment_core(
            video_file_path="nonexistent.mp4", duration=300.0, video_height=720, video_crf=18, video_fps=30
        )
        assert result is None  # Should fail due to non-existent file

    @mock.patch("subprocess.run")
    def test_encode_outro_segment_ffmpeg_failure(self, mock_subprocess, sample_video_path):
        """Test handling of ffmpeg execution failure."""
        if sample_video_path is None:
            pytest.skip("No sample video available")

        # Mock subprocess to raise CalledProcessError
        from subprocess import CalledProcessError

        mock_subprocess.side_effect = CalledProcessError(1, "ffmpeg", stderr="Mock error")

        result = encode_outro_segment_core(sample_video_path)
        assert result is None

    @mock.patch("subprocess.run")
    def test_encode_outro_segment_ffmpeg_not_found(self, mock_subprocess, sample_video_path):
        """Test handling when ffmpeg is not installed."""
        if sample_video_path is None:
            pytest.skip("No sample video available")

        # Mock subprocess to raise FileNotFoundError
        mock_subprocess.side_effect = FileNotFoundError("ffmpeg not found")

        result = encode_outro_segment_core(sample_video_path)
        assert result is None


class TestVideoEncodingComparison(TestVideoEncoding):
    """Tests comparing intro and outro encoding functionality."""

    @pytest.mark.integration
    def test_intro_and_outro_different_outputs(self, sample_video_path):
        """Test that intro and outro segments produce different outputs."""
        if sample_video_path is None:
            pytest.skip("No sample video available")

        # Encode intro segment
        intro_result = encode_intro_segment_core(
            video_file_path=sample_video_path, duration=3.0, video_height=240, video_fps=10
        )

        # Encode outro segment
        outro_result = encode_outro_segment_core(
            video_file_path=sample_video_path, duration=3.0, video_height=240, video_fps=10
        )

        if intro_result and outro_result:
            # Both should exist but be different files
            assert intro_result != outro_result
            assert os.path.exists(intro_result)
            assert os.path.exists(outro_result)
            assert "intro_segment_" in os.path.basename(intro_result)
            assert "outro_segment_" in os.path.basename(outro_result)

            # Cleanup
            for result in [intro_result, outro_result]:
                try:
                    temp_dir = os.path.dirname(result)
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass


# Test data setup instructions
def test_data_setup_instructions():
    """Instructions for setting up test data."""
    test_data_dir = Path(__file__).parent / "test_data"

    print(f"\n{'=' * 60}")
    print("TEST DATA SETUP INSTRUCTIONS")
    print(f"{'=' * 60}")
    print("To run integration tests, please create the directory:")
    print(f"  {test_data_dir}")
    print("\nThen add your test video files:")
    print(f"  {test_data_dir}/sample_video.mp4")
    print("\nRecommended test video characteristics:")
    print("  - Duration: At least 30 seconds (for testing both intro/outro)")
    print("  - Format: MP4 with H.264 video codec")
    print("  - Resolution: Any (will be scaled down during testing)")
    print("  - Size: Keep under 50MB for faster test execution")
    print("\nExample command to create test directory:")
    print(f"  mkdir -p {test_data_dir}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    test_data_setup_instructions()
