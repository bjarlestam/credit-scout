#!/usr/bin/env python3
"""
Test script for Credit Scout Agent

This script tests the movie analysis agent with the sample video.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Set a dummy API key for testing
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"
os.environ["GEMINI_API_KEY"] = "dummy-key-for-testing"

from credit_scout.movie_analysis_agent import analyze_movie
from rich.console import Console

console = Console()


async def main():
    """Test the movie analysis agent."""
    
    # Use the sample video
    sample_video = Path("tests/test_data/sample_video.mp4")
    
    if not sample_video.exists():
        console.print(f"[red]❌ Sample video not found: {sample_video}[/red]")
        return
    
    console.print(f"[blue]🎬 Testing Credit Scout with: {sample_video.name}[/blue]")
    console.print("[dim]This will test the complete workflow...[/dim]\n")
    
    try:
        # Run the analysis
        result = await analyze_movie(str(sample_video))
        
        # Display results
        console.print("\n[bold green]✅ Test Complete![/bold green]")
        console.print("=" * 60)
        console.print(result)
        console.print("=" * 60)
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    console.print("[bold blue]Credit Scout Agent Test[/bold blue]\n")
    asyncio.run(main()) 
