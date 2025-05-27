#!/usr/bin/env python3
"""
Tests for the save_analysis_results tool.
"""

import json

# Add src directory to Python path for testing
import sys
import tempfile
from pathlib import Path

import pytest

src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Import directly from the tool module to avoid API key requirements
from credit_scout.tools.save_analysis_results import parse_analysis_results, save_analysis_results


class TestParseAnalysisResults:
    """Test the parse_analysis_results function."""

    def test_parse_complete_results(self):
        """Test parsing complete analysis results."""
        analysis_text = """
        - **Intro ends at:** 01:09
        - **Outro starts at:** 09:49
        - **Total analysis cost:** $0.2967
        - **Confidence levels:**
          - Intro end detection confidence: 1.0 (high confidence)
          - Outro start detection confidence: 1.0 (high confidence)
        """

        results = parse_analysis_results(analysis_text)

        assert results["intro_end_time"] == "01:09"
        assert results["outro_start_time"] == "09:49"
        assert results["total_cost"] == 0.2967
        assert results["intro_confidence"] == 1.0
        assert results["outro_confidence"] == 1.0
        assert "analysis_timestamp" in results

    def test_parse_partial_results(self):
        """Test parsing partial analysis results."""
        analysis_text = """
        Intro ends at: 02:15
        Total cost: $0.045
        """

        results = parse_analysis_results(analysis_text)

        assert results["intro_end_time"] == "02:15"
        assert results["outro_start_time"] is None
        assert results["total_cost"] == 0.045
        assert results["intro_confidence"] is None
        assert results["outro_confidence"] is None

    def test_parse_no_matches(self):
        """Test parsing text with no matches."""
        analysis_text = "This is some random text with no timestamps or costs."

        results = parse_analysis_results(analysis_text)

        assert results["intro_end_time"] is None
        assert results["outro_start_time"] is None
        assert results["total_cost"] is None
        assert results["intro_confidence"] is None
        assert results["outro_confidence"] is None
        assert "analysis_timestamp" in results


class TestSaveAnalysisResults:
    """Test the save_analysis_results function."""

    def test_save_results_success(self):
        """Test successful saving of analysis results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary video file
            video_path = Path(temp_dir) / "test_movie.mp4"
            video_path.write_text("fake video content")

            analysis_text = """
            - **Intro ends at:** 01:09
            - **Outro starts at:** 09:49
            - **Total analysis cost:** $0.2967
            - **Confidence levels:**
              - Intro end detection confidence: 1.0 (high confidence)
              - Outro start detection confidence: 1.0 (high confidence)
            """

            # Save the results
            result = save_analysis_results.func(
                video_file_path=str(video_path), analysis_results=analysis_text, output_directory=temp_dir
            )

            # Check that the function returned success message
            assert "successfully saved" in result

            # Find the generated JSON file
            json_files = list(Path(temp_dir).glob("test_movie_analysis_*.json"))
            assert len(json_files) == 1

            json_path = json_files[0]

            # Verify the JSON content
            with open(json_path, "r") as f:
                saved_data = json.load(f)

            assert saved_data["intro_end_time"] == "01:09"
            assert saved_data["outro_start_time"] == "09:49"
            assert saved_data["total_cost"] == 0.2967
            assert saved_data["intro_confidence"] == 1.0
            assert saved_data["outro_confidence"] == 1.0
            assert saved_data["video_file"]["name"] == "test_movie.mp4"
            assert "analysis_timestamp" in saved_data

    def test_save_results_nonexistent_video(self):
        """Test saving results for a non-existent video file."""
        result = save_analysis_results.func(
            video_file_path="/nonexistent/path/movie.mp4", analysis_results="Some analysis text"
        )

        assert "Video file does not exist" in result

    def test_save_results_default_directory(self):
        """Test saving results to default directory (same as video)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary video file
            video_path = Path(temp_dir) / "test_movie.mp4"
            video_path.write_text("fake video content")

            analysis_text = "Intro ends at: 02:15"

            # Save the results without specifying output directory
            result = save_analysis_results.func(video_file_path=str(video_path), analysis_results=analysis_text)

            # Check that the function returned success message
            assert "successfully saved" in result

            # Find the generated JSON file in the same directory as the video
            json_files = list(Path(temp_dir).glob("test_movie_analysis_*.json"))
            assert len(json_files) == 1

    def test_filename_format(self):
        """Test that the JSON filename follows the expected format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary video file
            video_path = Path(temp_dir) / "my_awesome_movie.mp4"
            video_path.write_text("fake video content")

            analysis_text = "Intro ends at: 02:15"

            # Save the results
            save_analysis_results.func(
                video_file_path=str(video_path), analysis_results=analysis_text, output_directory=temp_dir
            )

            # Find the generated JSON file
            json_files = list(Path(temp_dir).glob("my_awesome_movie_analysis_*.json"))
            assert len(json_files) == 1

            json_filename = json_files[0].name
            # Should be in format: my_awesome_movie_analysis_YYYYMMDD_HHMMSS.json
            assert json_filename.startswith("my_awesome_movie_analysis_")
            assert json_filename.endswith(".json")
            assert len(json_filename) == len("my_awesome_movie_analysis_20241201_123456.json")


if __name__ == "__main__":
    pytest.main([__file__])
