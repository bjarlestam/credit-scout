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

    def detect_intro_times(self, video_file: types.File) -> Dict[str, float]:
        """Detect both the intro start and intro end timestamps in the intro segment."""
        logger.info("Detecting intro start and end timestamps...")
        console.print("[blue]🎯 Analyzing video for intro start and end times...[/blue]")

        model = "gemini-3-pro-preview"
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
                        text="""Analyze this video clip from the beginning of a film. 
                        Detect the start and end times of the intro sequence.
                        1. Identify the exact timestamp (in MM:SS format) where the intro sequence begins. The intro sequence may include the following elements:
                        - Studio logos and distributor cards (e.g., "splendid film").
                        - The main title card of the film itself (e.g., "BLACK BEAR").
                        2. Identify the exact timestamp (in MM:SS format) of where the intro ends. This is where the first scene of the main, continuous narrative body of the film begins. 
                        This point must occur after the full conclusion of ALL of the following elements:
All studio logos and distributor cards (e.g., "splendid film").
The main title card of the film itself (e.g., "BLACK BEAR").
All subsequent production company cards, "presents" cards, or "in association with" cards.
Essentially, I'm looking for the moment the film transitions from all opening textual and logo elements into the
primary storyline, not including any brief prologue or thematic vignette that might precede the main title."""
                    ),
                ],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="""Return the timestamps in MM:SS format. Do not include any other text or explanation.
                        For example, if the intro starts at 00:00 and ends at 00:45, simply return "
                        intro_start: 00:00
                        intro_end: 00:45"
                        """
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

            # Parse Gemini response for both timestamps
            text = response.text.strip()
            intro_start = None
            intro_end = None
            for line in text.splitlines():
                if line.lower().startswith("intro_start:"):
                    intro_start = line.split(":", 1)[1].strip()
                elif line.lower().startswith("intro_end:"):
                    intro_end = line.split(":", 1)[1].strip()
            if not intro_start or not intro_end:
                raise ValueError(f"Could not parse both intro_start and intro_end from Gemini response: {text}")

            logger.info(f"Intro start detected at: {intro_start}")
            logger.info(f"Intro end detected at: {intro_end}")
            console.print(f"[green]🎬 Intro starts at: {intro_start} | Intro ends at: {intro_end}[/green]")
            console.print(f"[dim]Total cost: ${cost_data['total_cost']:.6f}[/dim]")

            return {
                "intro_start": intro_start,
                "intro_end": intro_end,
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
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count

        input_cost_per_million = 4 if input_tokens > 200_000 else 2
        output_cost_per_million = 18 if input_tokens > 200_000 else 12

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


def detect_intro_times_core(video_file_path: str, api_key: Optional[str] = None) -> Optional[Dict[str, float]]:
    """
    Detect both the start and end time of the intro sequence in a video file using Gemini API.
    Args:
        video_file_path: Path to the input video file
        api_key: Optional Gemini API key (if not provided, uses GEMINI_API_KEY env var)
    Returns:
        Dictionary containing intro_start, intro_end, confidence, cost, and tokens_used, or None if detection failed
    """
    from pathlib import Path
    input_path = Path(video_file_path)
    if not input_path.exists():
        logger.error(f"Input video file does not exist: {video_file_path}")
        console.print(f"[red]❌ Input video file not found: {video_file_path}[/red]")
        return None
    if not input_path.is_file():
        logger.error(f"Input path is not a file: {video_file_path}")
        console.print(f"[red]❌ Input path is not a file: {video_file_path}[/red]")
        return None
    logger.info(f"Starting intro times detection for: {video_file_path}")
    console.print(f"[blue]🎬 Analyzing video: {input_path.name}[/blue]")
    try:
        client = GeminiClient(api_key=api_key)
        video_file = client.upload_and_process_file(video_file_path)
        try:
            result = client.detect_intro_times(video_file)
            logger.success(f"Successfully detected intro times: start={result['intro_start']}, end={result['intro_end']}")
            console.print("[green]✅ Intro times detection completed![/green]")
            return result
        finally:
            client.cleanup_file(video_file)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        console.print(f"[red]❌ Configuration error: {str(e)}[/red]")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during intro times detection: {str(e)}")
        console.print(f"[red]❌ Unexpected error: {str(e)}[/red]")
        return None


detect_intro_times = function_tool(detect_intro_times_core)
