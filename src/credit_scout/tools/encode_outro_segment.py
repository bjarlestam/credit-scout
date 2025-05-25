import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from agents import function_tool
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def encode_outro_segment_core(
    video_file_path: str,
    duration: float = 600.0,
    video_height: int = None,
    video_crf: int = None,
    video_fps: int = None,
) -> Optional[str]:
    """
    Encodes a low-resolution grayscale outro segment from the end of a video file.

    Args:
        video_file_path: Path to the input video file
        duration: Duration of the outro segment in seconds (default: 600.0 - 10 minutes)
        video_height: Height of the output video (default: from VIDEO_HEIGHT env var or 120)
        video_crf: Constant Rate Factor for video quality (default: from VIDEO_CRF env var or 28)
        video_fps: Frames per second for output video (default: from VIDEO_FPS env var or 5)

    Returns:
        Path to the encoded outro segment file, or None if encoding failed
    """

    # Set defaults from environment variables
    if video_height is None:
        video_height = int(os.environ.get("VIDEO_HEIGHT", "120"))
    if video_crf is None:
        video_crf = int(os.environ.get("VIDEO_CRF", "28"))
    if video_fps is None:
        video_fps = int(os.environ.get("VIDEO_FPS", "5"))

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

    # Create temporary directory for output
    temp_dir = tempfile.mkdtemp(prefix="credit_scout_outro_")
    output_filename = f"outro_segment_{input_path.stem}.mp4"
    output_path = os.path.join(temp_dir, output_filename)

    logger.info(f"Starting outro segment encoding for: {video_file_path}")
    logger.info(f"Output will be saved to: {output_path}")
    console.print(f"[blue]🎬 Processing video outro: {input_path.name}[/blue]")
    console.print(f"[dim]Output directory: {temp_dir}[/dim]")
    console.print(f"[dim]Extracting last {duration / 60:.1f} minutes[/dim]")

    # Build ffmpeg command - Extract and process the end of the video
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file
        "-sseof",
        f"-{duration}",  # Start from duration seconds before end
        "-i",
        str(input_path),
        "-vf",
        f"scale=trunc(oh*a/2)*2:{video_height},format=gray",
        "-c:v",
        "libx264",
        "-crf",
        str(video_crf),
        "-preset",
        "fast",
        "-r",
        str(video_fps),
        "-an",  # No audio
        output_path,
    ]

    logger.debug(f"FFmpeg command: {' '.join(cmd)}")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Encoding outro segment...", total=None)

            # Run ffmpeg command
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            progress.update(task, description="✅ Encoding completed")

        # Verify output file was created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.success(f"Successfully encoded outro segment: {output_path}")
            console.print("[green]✅ Outro segment created successfully![/green]")
            console.print(f"[dim]File size: {os.path.getsize(output_path):,} bytes[/dim]")
            return output_path
        else:
            logger.error("Output file was not created or is empty")
            console.print("[red]❌ Failed to create output file[/red]")
            return None

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg encoding failed with return code {e.returncode}")
        logger.error(f"FFmpeg stderr: {e.stderr}")
        console.print(f"[red]❌ Encoding failed: {e.stderr.strip() if e.stderr else 'Unknown error'}[/red]")
        return None
    except FileNotFoundError:
        logger.error("FFmpeg not found. Please ensure FFmpeg is installed and in PATH")
        console.print("[red]❌ FFmpeg not found. Please install FFmpeg and ensure it's in your PATH[/red]")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during encoding: {str(e)}")
        console.print(f"[red]❌ Unexpected error: {str(e)}[/red]")
        return None


encode_outro_segment = function_tool(encode_outro_segment_core)
