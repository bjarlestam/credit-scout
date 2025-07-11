import os
import time
from typing import Dict, Optional

import google.genai as genai
from agents import function_tool
from google.genai import types
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client with API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        self.client = self._initialize_client()

    def _initialize_client(self) -> genai.Client:
        """Initialize the Gemini client with API key."""
        return genai.Client(api_key=self.api_key)

    def upload_and_process_file(self, video_path: str) -> types.File:
        """Upload the video file to Gemini and wait for it to be processed."""
        try:
            # Try to upload the file and check its state
            logger.info(f"Uploading file to Gemini: {video_path}")
            console.print("[blue]📤 Uploading video to Gemini API...[/blue]")

            video_file = self.client.files.upload(file=str(video_path))
            logger.info(f"Uploaded file: {video_file.name} (State: {video_file.state.name})")
            console.print(f"[dim]File uploaded: {video_file.name}[/dim]")

            # Wait for the file to be processed
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Processing video...", total=None)

                while video_file.state.name == "PROCESSING":
                    logger.info(f"File {video_file.name} is still processing, waiting...")
                    time.sleep(5)
                    video_file = self.client.files.get(name=video_file.name)
                    logger.info(f"File state: {video_file.state.name}")

                progress.update(task, description="✅ Video processed")

            # Check if file is active
            if video_file.state.name != "ACTIVE":
                error_msg = f"File {video_file.name} is not in ACTIVE state (State: {video_file.state.name})"
                logger.error(error_msg)
                console.print(f"[red]❌ File processing failed: {video_file.state.name}[/red]")
                raise Exception(error_msg)

            console.print("[green]✅ Video ready for analysis[/green]")
            return video_file
        except Exception as e:
            logger.error(f"Error uploading or processing file: {e}")
            console.print(f"[red]❌ Upload failed: {str(e)}[/red]")
            raise

    def detect_credits_start(self, video_file: types.File) -> Dict[str, float]:
        """Detect the start timestamp of the end credits."""
        logger.info("Detecting end credits start timestamp...")
        console.print("[blue]🎯 Analyzing video for credits start time...[/blue]")

        model = "gemini-2.5-pro-preview-05-06"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=video_file.uri,
                        mime_type=video_file.mime_type,
                    ),
                ],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="""Please analyze this video clip, which includes the end of a film. Identify the exact
                        timestamp (in MM:SS format) where the main ending credits sequence begins.
This is typically characterized by:
The appearance of a list of names (e.g., cast, crew, departments, song titles).
These names usually scroll (often vertically from bottom to top) or are displayed on a series of static cards.
This sequence starts after the primary narrative of the film has clearly concluded.
The timestamp should mark the moment the first name/role of this main credit sequence appears on screen.
Please specifically exclude from this point:
Any final narrative scenes, epilogues, or "where are they now" segments, even if they lead directly into the credits or
have some text overlay.
Standalone "The End," "Fin," or similar concluding text cards that appear before the detailed credit list begins
 (unless these cards are stylistically integrated as the very first card of the credit roll itself).
Studio/distributor logos that might appear before the credits or after the credits have finished.
The start of any post-credits scenes (if the credits pause for a scene and then resume, I'm looking for the initial
 start of the main credit roll).
Essentially, I'm looking for the transition from the film's narrative closure to the formal listing of personnel and
 acknowledgments."""
                    ),
                ],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="""Only return the timestamp in MM:SS format. Do not include any other text or explanation.
                          For example, if the credits begin at 1 minute and 30 seconds, simply return "01:30"."""
                    ),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Analyzing with Gemini...", total=None)

                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                )

                progress.update(task, description="✅ Analysis completed")

            # Log token usage
            logger.info(f"Prompt token count: {response.usage_metadata.prompt_token_count}")
            logger.info(f"Candidates token count: {response.usage_metadata.candidates_token_count}")
            logger.info(f"Total token count: {response.usage_metadata.total_token_count}")

            cost_data = self.calculate_cost(response)
            logger.info(f"Input cost: ${cost_data['input_cost']:.6f}")
            logger.info(f"Output cost: ${cost_data['output_cost']:.6f}")
            logger.info(f"Total API call cost: ${cost_data['total_cost']:.6f}")

            timestamp = response.text.strip()
            logger.info(f"Credits start detected at: {timestamp}")
            console.print(f"[green]🎬 Credits start at: {timestamp}[/green]")
            console.print(f"[dim]Total cost: ${cost_data['total_cost']:.6f}[/dim]")

            return {
                "timestamp": timestamp,
                "confidence": 1.0,  # Default confidence
                "cost": cost_data["total_cost"],
                "tokens_used": response.usage_metadata.total_token_count,
            }
        except Exception as e:
            logger.error(f"Error during Gemini analysis: {e}")
            console.print(f"[red]❌ Analysis failed: {str(e)}[/red]")
            raise

    def calculate_cost(self, response) -> Dict[str, float]:
        """Calculate the cost of the API call based on token usage."""
        # Gemini 2.5 Pro Preview pricing (as of December 2024)
        # Input: $1.25 per 1M tokens (prompts <= 200k tokens)
        # Output: $10.00 per 1M tokens (prompts <= 200k tokens)
        # Note: For prompts > 200k tokens, rates are $2.50 input / $15.00 output
        input_cost_per_million = 1.25
        output_cost_per_million = 10.00

        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count

        input_cost = (input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * output_cost_per_million
        total_cost = input_cost + output_cost

        return {"input_cost": input_cost, "output_cost": output_cost, "total_cost": total_cost}

    def cleanup_file(self, video_file: types.File) -> None:
        """Clean up the uploaded file from Gemini."""
        try:
            self.client.files.delete(name=video_file.name)
            logger.info(f"Cleaned up uploaded file: {video_file.name}")
            console.print("[dim]🗑️ Cleaned up uploaded file[/dim]")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {video_file.name}: {e}")


def detect_outro_start_time_core(
    outro_segment_path: str, 
    total_video_duration: int, 
    outro_segment_duration: float = 600.0,
    api_key: Optional[str] = None
) -> Optional[Dict[str, float]]:
    """
    Detect the start time of the end credits sequence in an outro segment and return the absolute timestamp.

    Args:
        outro_segment_path: Path to the encoded outro segment file
        total_video_duration: Total duration of the original video in seconds
        outro_segment_duration: Duration of the outro segment in seconds (default: 600.0)
        api_key: Optional Gemini API key (if not provided, uses GEMINI_API_KEY env var)

    Returns:
        Dictionary containing absolute timestamp, confidence, cost, and tokens_used, or None if detection failed
    """
    from pathlib import Path

    # Validate input file
    input_path = Path(outro_segment_path)
    if not input_path.exists():
        logger.error(f"Input outro segment file does not exist: {outro_segment_path}")
        console.print(f"[red]❌ Input outro segment file not found: {outro_segment_path}[/red]")
        return None

    if not input_path.is_file():
        logger.error(f"Input path is not a file: {outro_segment_path}")
        console.print(f"[red]❌ Input path is not a file: {outro_segment_path}[/red]")
        return None

    logger.info(f"Starting credits start time detection for outro segment: {outro_segment_path}")
    logger.info(f"Total video duration: {total_video_duration} seconds")
    console.print(f"[blue]🎬 Analyzing outro segment: {input_path.name}[/blue]")
    console.print(f"[dim]Total video duration: {total_video_duration} seconds[/dim]")

    # Calculate the start position of the outro segment in the full video
    outro_start_in_full_video = int(total_video_duration - outro_segment_duration)
    logger.info(f"Outro segment starts at {outro_start_in_full_video} seconds in the full video")

    try:
        # Initialize Gemini client
        client = GeminiClient(api_key=api_key)

        # Upload and process the outro segment file
        video_file = client.upload_and_process_file(outro_segment_path)

        try:
            # Detect the credits start timestamp in the outro segment
            result = client.detect_credits_start(video_file)
            
            # Parse the relative timestamp from the segment
            relative_timestamp = result['timestamp']
            logger.info(f"Credits start detected at {relative_timestamp} in outro segment")
            
            # Convert MM:SS to seconds
            def parse_timestamp(timestamp_str: str) -> int:
                parts = timestamp_str.split(':')
                if len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    return minutes * 60 + seconds
                else:
                    raise ValueError(f"Invalid timestamp format: {timestamp_str}")
            
            relative_seconds = parse_timestamp(relative_timestamp)
            
            # Calculate absolute timestamp in the full video
            absolute_seconds = int(outro_start_in_full_video + relative_seconds)
            
            # Convert back to MM:SS format
            abs_minutes = absolute_seconds // 60
            abs_seconds_remainder = absolute_seconds % 60
            absolute_timestamp = f"{abs_minutes:02d}:{abs_seconds_remainder:02d}"
            
            logger.success(f"Credits start at {relative_timestamp} in segment, {absolute_timestamp} in full video")
            console.print(f"[green]🎬 Credits start at: {absolute_timestamp} (absolute time in full video)[/green]")
            console.print(f"[dim]Relative time in segment: {relative_timestamp}[/dim]")
            console.print(f"[dim]Total cost: ${result['cost']:.6f}[/dim]")

            # Return the result with absolute timestamp
            return {
                "timestamp": absolute_timestamp,
                "relative_timestamp": relative_timestamp,
                "absolute_seconds": absolute_seconds,
                "confidence": result['confidence'],
                "cost": result['cost'],
                "tokens_used": result['tokens_used'],
            }

        finally:
            # Always cleanup the uploaded file
            client.cleanup_file(video_file)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        console.print(f"[red]❌ Configuration error: {str(e)}[/red]")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during credits start time detection: {str(e)}")
        console.print(f"[red]❌ Unexpected error: {str(e)}[/red]")
        return None


detect_outro_start_time = function_tool(detect_outro_start_time_core)
