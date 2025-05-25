#!/usr/bin/env python3
"""
Credit Scout - AI agent for movie credit detection

Main CLI entry point for the credit-scout package.
"""

import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

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
    console.print("  credit-scout <movie_file_path>")
    console.print("\n[bold]Example:[/bold]")
    console.print("  credit-scout /path/to/movie.mp4")
    console.print("\n[bold]Supported formats:[/bold]")
    console.print("  MP4, AVI, MKV, MOV, and other common video formats")
    console.print("\n[bold]Requirements:[/bold]")
    console.print("  - OPENAI_API_KEY environment variable or in .env file")
    console.print("  - GEMINI_API_KEY environment variable or in .env file")
    console.print("  - FFmpeg installed and available in PATH")


async def run_analysis(movie_file_path: str):
    """Run the movie analysis."""
    try:
        # Handle both direct execution and package execution
        try:
            from credit_scout.movie_analysis_agent import analyze_movie
        except ImportError:
            # If running directly, add the src directory to path
            import sys as local_sys
            from pathlib import Path as LocalPath
            src_dir = LocalPath(__file__).parent.parent
            local_sys.path.insert(0, str(src_dir))
            from credit_scout.movie_analysis_agent import analyze_movie
        
        # Run the analysis
        console.print(f"\n[blue]🎬 Analyzing movie: {Path(movie_file_path).name}[/blue]")
        console.print("[dim]This may take several minutes depending on the video size...[/dim]\n")
        
        result = await analyze_movie(movie_file_path)
        # Display results in a nice panel
        console.print("\n")
        console.print(Panel(
            result,
            title="[bold green]Analysis Results[/bold green]",
            border_style="green"
        ))
        
    except ImportError as e:
        console.print(f"[red]❌ Import error: {str(e)}[/red]")
        console.print("[yellow]Make sure all dependencies are installed[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Analysis failed: {str(e)}[/red]")
        sys.exit(1)


def cli() -> None:
    """Main CLI entry point."""
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
    
    try:
        asyncio.run(run_analysis(movie_file_path))
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Analysis interrupted by user[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
