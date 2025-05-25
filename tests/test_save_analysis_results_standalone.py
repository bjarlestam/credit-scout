#!/usr/bin/env python3
"""
Standalone tests for the save_analysis_results tool.
"""

import json
import tempfile
from pathlib import Path
import sys

# Add src directory to Python path for testing
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Import the module directly to avoid API key requirements
sys.path.insert(0, str(src_dir / "credit_scout" / "tools"))
import save_analysis_results as sar_module
parse_analysis_results = sar_module.parse_analysis_results
# Get the actual function from the FunctionTool
save_analysis_results_func = sar_module.save_analysis_results.func


def test_parse_complete_results():
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
    
    # Debug prints
    print(f"Debug - parsed results: {results}")
    print(f"Debug - analysis text: {repr(analysis_text)}")
    
    assert results["intro_end_time"] == "01:09"
    assert results["outro_start_time"] == "09:49"
    assert results["total_cost"] == 0.2967
    assert results["intro_confidence"] == 1.0
    assert results["outro_confidence"] == 1.0
    assert "analysis_timestamp" in results
    print("✅ test_parse_complete_results passed")


def test_parse_partial_results():
    """Test parsing partial analysis results."""
    analysis_text = """
    Intro ends at: 02:15
    Total cost: $0.045
    """
    
    results = parse_analysis_results(analysis_text)
    
    # Debug prints
    print(f"Debug - partial results: {results}")
    print(f"Debug - partial text: {repr(analysis_text)}")
    
    assert results["intro_end_time"] == "02:15"
    assert results["outro_start_time"] is None
    assert results["total_cost"] == 0.045
    assert results["intro_confidence"] is None
    assert results["outro_confidence"] is None
    print("✅ test_parse_partial_results passed")


def test_save_results_success():
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
        result = save_analysis_results_func(
            video_file_path=str(video_path),
            analysis_results=analysis_text,
            output_directory=temp_dir
        )
        
        # Check that the function returned success message
        assert "successfully saved" in result
        
        # Find the generated JSON file
        json_files = list(Path(temp_dir).glob("test_movie_analysis_*.json"))
        assert len(json_files) == 1
        
        json_path = json_files[0]
        
        # Verify the JSON content
        with open(json_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["intro_end_time"] == "01:09"
        assert saved_data["outro_start_time"] == "09:49"
        assert saved_data["total_cost"] == 0.2967
        assert saved_data["intro_confidence"] == 1.0
        assert saved_data["outro_confidence"] == 1.0
        assert saved_data["video_file"]["name"] == "test_movie.mp4"
        assert "analysis_timestamp" in saved_data
        
        print(f"✅ test_save_results_success passed - JSON saved to {json_path.name}")


def test_filename_format():
    """Test that the JSON filename follows the expected format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary video file
        video_path = Path(temp_dir) / "my_awesome_movie.mp4"
        video_path.write_text("fake video content")
        
        analysis_text = "Intro ends at: 02:15"
        
        # Save the results
        save_analysis_results_func(
            video_file_path=str(video_path),
            analysis_results=analysis_text,
            output_directory=temp_dir
        )
        
        # Find the generated JSON file
        json_files = list(Path(temp_dir).glob("my_awesome_movie_analysis_*.json"))
        assert len(json_files) == 1
        
        json_filename = json_files[0].name
        # Should be in format: my_awesome_movie_analysis_YYYYMMDD_HHMMSS.json
        assert json_filename.startswith("my_awesome_movie_analysis_")
        assert json_filename.endswith(".json")
        
        print(f"✅ test_filename_format passed - filename: {json_filename}")


if __name__ == "__main__":
    print("Running standalone tests for save_analysis_results...")
    
    try:
        test_parse_complete_results()
        test_parse_partial_results()
        test_save_results_success()
        test_filename_format()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 