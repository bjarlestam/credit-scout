import asyncio
import os
from pathlib import Path

from agents import Agent, Runner, trace
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console

# Import all the available function tools
try:
    from credit_scout.tools.detect_intro_times import detect_intro_times
    from credit_scout.tools.detect_outro_start_time import detect_outro_start_time
    from credit_scout.tools.encode_intro_segment import encode_intro_segment
    from credit_scout.tools.encode_outro_segment import encode_outro_segment
    from credit_scout.tools.get_video_duration import get_video_duration
    from credit_scout.tools.save_analysis_results import save_analysis_results
except ImportError:
    # Handle direct execution by adding src to path
    import sys

    src_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(src_dir))
    from credit_scout.tools.detect_intro_times import detect_intro_times
    from credit_scout.tools.detect_outro_start_time import detect_outro_start_time
    from credit_scout.tools.encode_intro_segment import encode_intro_segment
    from credit_scout.tools.encode_outro_segment import encode_outro_segment
    from credit_scout.tools.get_video_duration import get_video_duration
    from credit_scout.tools.save_analysis_results import save_analysis_results

console = Console()

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
dotenv_path = os.path.join(project_root, ".env")

# Try to load from .env file
load_dotenv(dotenv_path)

# Check if required API keys are set
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not openai_api_key:
    console.print(f"[yellow]Warning: OPENAI_API_KEY not found in {dotenv_path}[/yellow]")
    console.print("Please set your OPENAI_API_KEY in the .env file or as an environment variable")
    console.print("Example .env file content: OPENAI_API_KEY=your-api-key-here")
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file or environment.")

if not gemini_api_key:
    console.print(f"[yellow]Warning: GEMINI_API_KEY not found in {dotenv_path}[/yellow]")
    console.print("Please set your GEMINI_API_KEY in the .env file or as an environment variable")
    console.print("Example .env file content: GEMINI_API_KEY=your-api-key-here")
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file or environment.")

console.print(f"[green]✅ API keys loaded successfully from {dotenv_path}[/green]")

# Define the tools available to the agent
MOVIE_ANALYSIS_TOOLS = [
    get_video_duration,
    encode_intro_segment,
    encode_outro_segment,
    detect_intro_times,
    detect_outro_start_time,
    save_analysis_results,
]

# Create the movie analysis agent
agent = Agent(
    name="MovieAnalysisAgent",
    instructions=(
        "You are a specialized movie analysis agent that determines the intro start time, intro end time, and outro start time "
        "for movie files. Your goal is to provide accurate timestamps for when the intro sequence begins, when the main movie content begins, "
        "and when the end credits start.\n\n"
        "Follow this precise workflow:\n\n"
        "1. **Get Video Duration**: Use `get_video_duration` to determine the total duration of the movie file. "
        "This is essential for calculating segment positions and absolute timestamps.\n\n"
        "2. **Analyze Intro**: \n"
        "   - Use `encode_intro_segment` to create a low-resolution segment from the beginning of the movie "
        "     (default: first 5 minutes). This optimizes the analysis for speed and cost.\n"
        "   - Use `detect_intro_times` with the encoded intro segment to determine both when the intro sequence begins (first logo/title) "
        "     and when the main movie content begins (after all logos, titles, and opening credits).\n\n"
        "3. **Analyze Outro**: \n"
        "   - Use `encode_outro_segment` to create a low-resolution segment from the end of the movie "
        "     (default: last 10 minutes). This captures the transition from movie to credits.\n"
        "   - Use `detect_outro_start_time` with the encoded outro segment and total video duration to "
        "     determine when the end credits begin. This function returns the absolute timestamp in the full video.\n\n"
        "4. **Save Results**: After completing the analysis, use `save_analysis_results` to save the "
        "complete analysis results to a JSON file. This creates a structured record with the video filename "
        "and current date in the filename.\n\n"
        "**Important Notes:**\n"
        "- The intro analysis works on an encoded segment of the intro for efficiency and maximum accuracy\n"
        "- The outro analysis works on an encoded segment of the outro for efficiency, but return absolute timestamps\n"
        "- All timestamps should be in MM:SS format\n"
        "- Handle errors gracefully and provide clear feedback about any failures\n"
        "- Report the intro start time, intro end time, and outro start time in your final response\n"
        "- Include cost information and confidence levels when available\n"
        "- Always save the results to a JSON file for future reference\n\n"
        "Your final response should clearly state:\n"
        "- Intro starts at: [timestamp]\n"
        "- Intro ends at: [timestamp]\n"
        "- Outro starts at: [timestamp]\n"
        "- Total analysis cost: [cost]\n"
        "- Any relevant confidence or quality information\n"
        "- Confirmation that results have been saved to JSON file"
    ),
    tools=MOVIE_ANALYSIS_TOOLS,
    model="gpt-4o-mini",
)


async def analyze_movie(movie_file_path: str) -> str:
    """
    Analyze a movie file to determine intro end time and outro start time.

    Args:
        movie_file_path: Path to the movie file to analyze

    Returns:
        Analysis results as a string
    """
    # Validate input file
    input_path = Path(movie_file_path)
    if not input_path.exists():
        error_msg = f"Movie file does not exist: {movie_file_path}"
        logger.error(error_msg)
        console.print(f"[red]❌ {error_msg}[/red]")
        return error_msg

    if not input_path.is_file():
        error_msg = f"Path is not a file: {movie_file_path}"
        logger.error(error_msg)
        console.print(f"[red]❌ {error_msg}[/red]")
        return error_msg

    console.print(f"[blue]🎬 Starting movie analysis for: {input_path.name}[/blue]")
    logger.info(f"Starting movie analysis for: {movie_file_path}")

    try:
        with trace("Analyzing movie for intro and outro timestamps..."):
            result = await Runner.run(
                agent,
                f"Analyze the movie file at '{movie_file_path}' to determine both the intro start time, intro end time, "
                f"and outro start time. Follow the complete workflow: get video duration, encode segments "
                f"as needed, and detect both intro start, intro end, and outro start timestamps. Provide a comprehensive "
                f"analysis with clear timestamps and cost information.",
            )

            logger.info("Movie analysis completed successfully")
            console.print("[green]✅ Movie analysis completed![/green]")
            return result.final_output

    except Exception as e:
        error_msg = f"Error during movie analysis: {str(e)}"
        logger.error(error_msg)
        console.print(f"[red]❌ {error_msg}[/red]")
        return error_msg


async def main():
    """Main function for testing the movie analysis agent."""
    import sys

    if len(sys.argv) != 2:
        console.print("[yellow]Usage: python movie_analysis_agent.py <movie_file_path>[/yellow]")
        console.print("[dim]Example: python movie_analysis_agent.py /path/to/movie.mp4[/dim]")
        return

    movie_file_path = sys.argv[1]
    result = await analyze_movie(movie_file_path)
    console.print("\n[bold]Analysis Results:[/bold]")
    console.print(result)


if __name__ == "__main__":
    asyncio.run(main())
