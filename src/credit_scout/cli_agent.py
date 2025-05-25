#!/usr/bin/env python3
"""
Credit Scout Movie Analysis CLI

A command-line interface for analyzing movies to detect intro end times and outro start times.
"""

import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from credit_scout.movie_analysis_agent import analyze_movie

console = Console()


def print_banner():
    """Print the application banner."""
    banner = """
[bold blue]Credit Scout[/bold blue] [dim]v0.1.0[/dim]
[dim]AI-powered movie intro and outro detection[/dim]
    """
    console.print(Panel(banner, border_style="blue"))


def print_usage():
    """Print usage information."""
    console.print("\n[bold]Usage:[/bold]")
    console.print("  python -m credit_scout.cli_agent <movie_file_path>")
    console.print("\n[bold]Example:[/bold]")
    console.print("  python -m credit_scout.cli_agent /path/to/movie.mp4")
    console.print("\n[bold]Supported formats:[/bold]")
    console.print("  MP4, AVI, MKV, MOV, and other common video formats")
    console.print("\n[bold]Requirements:[/bold]")
    console.print("  - OPENAI_API_KEY environment variable or in .env file")
    console.print("  - GEMINI_API_KEY environment variable or in .env file")
    console.print("  - FFmpeg installed and available in PATH")


async def main():
    """Main CLI function."""
    print_banner()
    
    if len(sys.argv) != 2:
        console.print("[red]❌ Error: Movie file path is required[/red]")
        print_usage()
        sys.exit(1)
    
    movie_file_path = sys.argv[1]
    
    # Validate file exists
    if not Path(movie_file_path).exists():
        console.print(f"[red]❌ Error: File not found: {movie_file_path}[/red]")
        sys.exit(1)
    
    # Run the analysis
    console.print(f"\n[blue]🎬 Analyzing movie: {Path(movie_file_path).name}[/blue]")
    console.print("[dim]This may take several minutes depending on the video size...[/dim]\n")
    
    try:
        result = await analyze_movie(movie_file_path)
        
        # Display results in a nice panel
        console.print("\n")
        console.print(Panel(
            result,
            title="[bold green]Analysis Results[/bold green]",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Analysis interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Analysis failed: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 