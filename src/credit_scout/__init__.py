"""
Credit Scout - AI agent for movie credit detection

A sophisticated movie analysis tool that uses AI to automatically detect
intro end times and outro start times in movie files.
"""

from .__version__ import __version__

# Import main functionality
try:
    from .movie_analysis_agent import analyze_movie  # noqa: F401
    from .tools import (  # noqa: F401
        detect_intro_times,
        detect_outro_start_time,
        encode_intro_segment,
        encode_outro_segment,
        get_video_duration,
        save_analysis_results,
    )
    
    __all__ = [
        "__version__",
        "analyze_movie",
        "detect_intro_times",
        "detect_outro_start_time",
        "encode_intro_segment", 
        "encode_outro_segment",
        "get_video_duration",
        "save_analysis_results",
    ]
except ImportError:
    # Handle cases where dependencies might not be available
    __all__ = ["__version__"]
