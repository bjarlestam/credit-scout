"""
Credit Scout Tools

This package contains all the function tools used by the Credit Scout agent
for movie analysis and credit detection.
"""

from .detect_intro_times import detect_intro_times, detect_intro_times
from .detect_outro_start_time import detect_outro_start_time
from .encode_intro_segment import encode_intro_segment
from .encode_outro_segment import encode_outro_segment
from .get_video_duration import get_video_duration
from .save_analysis_results import save_analysis_results

__all__ = [
    "detect_intro_times",
    "detect_outro_start_time", 
    "encode_intro_segment",
    "encode_outro_segment",
    "get_video_duration",
    "save_analysis_results",
] 