import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from agents import function_tool
from loguru import logger
from rich.console import Console

console = Console()


def parse_analysis_results(analysis_text: str) -> Dict:
    """
    Parse the analysis results text to extract structured data.

    Args:
        analysis_text: The raw analysis results text

    Returns:
        Dictionary containing parsed results
    """
    results = {
        "intro_start_time": None,
        "intro_end_time": None,
        "outro_start_time": None,
        "total_cost": None,
        "intro_confidence": None,
        "outro_confidence": None,
        "analysis_timestamp": datetime.now().isoformat(),
    }

    console.print("[bold green]Analysis text:[/bold green]")
    console.print(analysis_text)

    # Extract intro start time
    intro_start_match = re.search(r"(?:\*\*)?Intro starts at:?\*?\*?\s*(\d{1,2}:\d{2})", analysis_text, re.IGNORECASE)
    if intro_start_match:
        results["intro_start_time"] = intro_start_match.group(1)

    # Extract intro end time
    intro_end_match = re.search(r"(?:\*\*)?Intro ends at:?\*?\*?\s*(\d{1,2}:\d{2})", analysis_text, re.IGNORECASE)
    if intro_end_match:
        results["intro_end_time"] = intro_end_match.group(1)

    # Extract outro start time
    outro_match = re.search(r"(?:\*\*)?Outro starts at:?\*?\*?\s*(\d{1,2}:\d{2})", analysis_text, re.IGNORECASE)
    if outro_match:
        results["outro_start_time"] = outro_match.group(1)

    # Extract total cost (handle both markdown and plain text formats)
    cost_match = re.search(r"(?:\*\*)?Total (?:analysis )?cost:?\*?\*?\s*\$?([\d.]+)", analysis_text, re.IGNORECASE)
    if cost_match:
        results["total_cost"] = float(cost_match.group(1))

    # Extract intro confidence
    intro_conf_match = re.search(r"Intro (?:end )?detection confidence:\s*([\d.]+)", analysis_text, re.IGNORECASE)
    if intro_conf_match:
        results["intro_confidence"] = float(intro_conf_match.group(1))

    # Extract outro confidence
    outro_conf_match = re.search(r"Outro start detection confidence:\s*([\d.]+)", analysis_text, re.IGNORECASE)
    if outro_conf_match:
        results["outro_confidence"] = float(outro_conf_match.group(1))

    return results


@function_tool
def save_analysis_results(video_file_path: str, analysis_results: str, output_directory: Optional[str] = None) -> str:
    """
    Save movie analysis results to a JSON file.

    The JSON file will be named with the video filename and current date,
    and will contain structured data about intro/outro timestamps, costs, and confidence levels.

    Args:
        video_file_path: Path to the original video file
        analysis_results: The analysis results text to parse and save
        output_directory: Optional directory to save the JSON file (defaults to same directory as video)

    Returns:
        Path to the saved JSON file
    """
    try:
        # Validate input video file
        video_path = Path(video_file_path)
        if not video_path.exists():
            error_msg = f"Video file does not exist: {video_file_path}"
            logger.error(error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            return error_msg

        # Parse the analysis results
        parsed_results = parse_analysis_results(analysis_results)

        # Add video file information
        parsed_results["video_file"] = {
            "name": video_path.name,
            "path": str(video_path.absolute()),
            "size_bytes": video_path.stat().st_size if video_path.exists() else None,
        }

        # Determine output directory
        if output_directory:
            output_dir = Path(output_directory)
        else:
            output_dir = video_path.parent

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with video name and date
        video_stem = video_path.stem  # filename without extension
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"{video_stem}_analysis_{current_date}.json"
        json_path = output_dir / json_filename

        # Save the JSON file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Analysis results saved to: {json_path}")
        console.print(f"[green]💾 Analysis results saved to: {json_path.name}[/green]")

        return f"Analysis results successfully saved to: {str(json_path)}"

    except Exception as e:
        error_msg = f"Failed to save analysis results: {str(e)}"
        logger.error(error_msg)
        console.print(f"[red]❌ {error_msg}[/red]")
        return error_msg
