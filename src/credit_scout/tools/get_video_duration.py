import subprocess
from pathlib import Path
from typing import Optional

from agents import function_tool
from loguru import logger
from rich.console import Console

console = Console()


def get_video_duration_core(video_file_path: str) -> Optional[int]:
    """
    Get the duration of a video file in seconds using ffprobe.

    Args:
        video_file_path: Path to the input video file

    Returns:
        Duration in seconds as an integer, or None if detection failed
    """
    # Validate input file
    input_path = Path(video_file_path)
    if not input_path.exists():
        logger.error(f"Input video file does not exist: {video_file_path}")
        console.print(f"[red]❌ Input video file not found: {video_file_path}[/red]")
        return None

    if not input_path.is_file():
        logger.error(f"Input path is not a file: {video_file_path}")
        console.print(f"[red]❌ Input path is not a file: {video_file_path}[/red]")
        return None

    logger.info(f"Getting video duration for: {video_file_path}")
    console.print(f"[blue]📏 Analyzing video duration: {input_path.name}[/blue]")

    # Build ffprobe command
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]

    logger.debug(f"FFprobe command: {' '.join(cmd)}")

    try:
        # Run ffprobe command
        process = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Log stderr if present (even for successful runs, ffprobe might output warnings)
        if process.stderr:
            logger.info(f"FFprobe stderr: {process.stderr.strip()}")

        # Check for errors
        if process.returncode != 0:
            logger.error(f"FFprobe failed with return code {process.returncode}")
            logger.error(f"FFprobe stderr: {process.stderr}")
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            console.print(f"[red]❌ FFprobe failed: {error_msg}[/red]")
            return None

        # Parse duration
        duration_str = process.stdout.strip()
        if not duration_str:
            logger.error("FFprobe returned empty duration")
            console.print("[red]❌ Could not determine video duration[/red]")
            return None

        try:
            duration_float = float(duration_str)
            duration_seconds = int(duration_float)

            logger.success(
                f"Successfully determined video duration: {duration_seconds} seconds ({duration_float:.2f}s)"
            )
            console.print(f"[green]✅ Video duration: {duration_seconds} seconds ({duration_float:.2f}s)[/green]")

            # Convert to human-readable format for display
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60

            if hours > 0:
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                time_str = f"{minutes:02d}:{seconds:02d}"

            console.print(f"[dim]Human readable: {time_str}[/dim]")

            return duration_seconds

        except ValueError:
            logger.error(f"Could not parse duration as float: {duration_str}")
            console.print(f"[red]❌ Invalid duration format: {duration_str}[/red]")
            return None

    except FileNotFoundError:
        logger.error("FFprobe not found. Please ensure FFmpeg is installed and in PATH")
        console.print("[red]❌ FFprobe not found. Please install FFmpeg and ensure it's in your PATH[/red]")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during duration detection: {str(e)}")
        console.print(f"[red]❌ Unexpected error: {str(e)}[/red]")
        return None


get_video_duration = function_tool(get_video_duration_core)
