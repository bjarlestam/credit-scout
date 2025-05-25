#!/usr/bin/env python3
"""
Example: Movie Analysis with Credit Scout

This example demonstrates how to use the Credit Scout movie analysis agent
to detect intro end times and outro start times in movie files.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import credit_scout
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from credit_scout.movie_analysis_agent import analyze_movie
from rich.console import Console

console = Console()


async def main():
    """Example usage of the movie analysis agent."""
    
    # Example movie file path - replace with your actual movie file
    movie_file_path = "/path/to/your/movie.mp4"
    
    # Check if the example file exists
    if not Path(movie_file_path).exists():
        console.print("[yellow]⚠️  Example movie file not found![/yellow]")
        console.print(f"[dim]Please update the movie_file_path variable in {__file__}[/dim]")
        console.print("[dim]Or provide a movie file path as a command line argument[/dim]")
        
        # Check if a file path was provided as argument
        if len(sys.argv) > 1:
            movie_file_path = sys.argv[1]
            if not Path(movie_file_path).exists():
                console.print(f"[red]❌ File not found: {movie_file_path}[/red]")
                return
        else:
            return
    
    console.print(f"[blue]🎬 Starting analysis of: {Path(movie_file_path).name}[/blue]")
    console.print("[dim]This example will analyze the movie to find intro and outro timestamps[/dim]\n")
    
    try:
        # Run the movie analysis
        result = await analyze_movie(movie_file_path)
        
        # Display the results
        console.print("\n[bold green]✅ Analysis Complete![/bold green]")
        console.print("=" * 60)
        console.print(result)
        console.print("=" * 60)
        
    except Exception as e:
        console.print(f"[red]❌ Analysis failed: {str(e)}[/red]")
        console.print("[yellow]Make sure you have:[/yellow]")
        console.print("  - OPENAI_API_KEY set in your environment or .env file")
        console.print("  - GEMINI_API_KEY set in your environment or .env file")
        console.print("  - FFmpeg installed and available in PATH")


if __name__ == "__main__":
    # Set up environment variables if needed
    console.print("[bold blue]Credit Scout Movie Analysis Example[/bold blue]\n")
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]⚠️  OPENAI_API_KEY not found in environment[/yellow]")
        console.print("[dim]Make sure to set it in your .env file or environment[/dim]")
    
    if not os.getenv("GEMINI_API_KEY"):
        console.print("[yellow]⚠️  GEMINI_API_KEY not found in environment[/yellow]")
        console.print("[dim]Make sure to set it in your .env file or environment[/dim]")
    
    # Run the example
    asyncio.run(main()) 