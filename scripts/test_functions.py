#!/usr/bin/env python3
"""
Manual testing script for credit-scout functions.

Usage:
    uv run scripts/test_functions.py encode_intro <video_path> [--duration 300] [--height 360] [--fps 15]
    uv run scripts/test_functions.py encode_outro <video_path> [--duration 600] [--height 360] [--fps 15]
    uv run scripts/test_functions.py detect_intro <video_path> [--api-key YOUR_KEY]
    uv run scripts/test_functions.py detect_outro <video_path> [--duration 600] [--api-key YOUR_KEY]
    uv run scripts/test_functions.py get_duration <video_path>
    uv run scripts/test_functions.py --help

Examples:
    uv run scripts/test_functions.py encode_intro /path/to/video.mp4
    uv run scripts/test_functions.py encode_outro /path/to/video.mp4 --duration 300
    uv run scripts/test_functions.py detect_intro /path/to/video.mp4
    uv run scripts/test_functions.py detect_outro /path/to/video.mp4 --duration 600
    uv run scripts/test_functions.py get_duration /path/to/video.mp4
"""

import argparse
import os
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from credit_scout.tools.detect_intro_end_time import detect_intro_end_time_core
from credit_scout.tools.detect_outro_start_time import detect_outro_start_time_core
from credit_scout.tools.encode_intro_segment import encode_intro_segment_core
from credit_scout.tools.encode_outro_segment import encode_outro_segment_core
from credit_scout.tools.get_video_duration import get_video_duration_core


def test_encode_intro(args):
    """Test the intro segment encoding function."""
    print(f"🎬 Testing intro segment encoding for: {args.video_path}")
    print(f"Parameters: duration={args.duration}s, height={args.height}px, fps={args.fps}")
    print("-" * 60)
    
    result = encode_intro_segment_core(
        video_file_path=args.video_path,
        duration=args.duration,
        video_height=args.height,
        video_crf=args.crf,
        video_fps=args.fps
    )
    
    if result:
        print(f"\n✅ Success! Encoded intro segment saved to: {result}")
        print(f"File size: {os.path.getsize(result):,} bytes")
    else:
        print("\n❌ Failed to encode intro segment")
        sys.exit(1)


def test_encode_outro(args):
    """Test the outro segment encoding function."""
    print(f"🎬 Testing outro segment encoding for: {args.video_path}")
    print(f"Parameters: duration={args.duration}s, height={args.height}px, fps={args.fps}")
    print("-" * 60)
    
    result = encode_outro_segment_core(
        video_file_path=args.video_path,
        duration=args.duration,
        video_height=args.height,
        video_crf=args.crf,
        video_fps=args.fps
    )
    
    if result:
        print(f"\n✅ Success! Encoded outro segment saved to: {result}")
        print(f"File size: {os.path.getsize(result):,} bytes")
    else:
        print("\n❌ Failed to encode outro segment")
        sys.exit(1)


def test_detect_intro(args):
    """Test the intro end time detection function."""
    print(f"🎯 Testing intro end time detection for: {args.video_path}")
    if args.api_key:
        print("Using provided API key")
    elif os.getenv("GEMINI_API_KEY"):
        print("Using GEMINI_API_KEY from environment")
    else:
        print("❌ No API key provided. Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    print("-" * 60)
    
    result = detect_intro_end_time_core(
        video_file_path=args.video_path,
        api_key=args.api_key
    )
    
    if result:
        print("\n✅ Success! Intro end time detection completed:")
        print(f"  Timestamp: {result['timestamp']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Cost: ${result['cost']:.6f}")
        print(f"  Tokens used: {result['tokens_used']:,}")
    else:
        print("\n❌ Failed to detect intro end time")
        sys.exit(1)


def test_detect_outro(args):
    """Test the outro/credits start time detection function."""
    print(f"🎯 Testing credits start time detection for: {args.video_path}")
    if args.api_key:
        print("Using provided API key")
    elif os.getenv("GEMINI_API_KEY"):
        print("Using GEMINI_API_KEY from environment")
    else:
        print("❌ No API key provided. Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    print("-" * 60)
    
    # First, we need to encode the outro segment and get video duration
    print("Step 1: Getting video duration...")
    total_duration = get_video_duration_core(video_file_path=args.video_path)
    if total_duration is None:
        print("❌ Failed to get video duration")
        sys.exit(1)
    
    print(f"Step 2: Encoding outro segment (last {args.duration} seconds)...")
    outro_segment_path = encode_outro_segment_core(
        video_file_path=args.video_path,
        duration=args.duration
    )
    if outro_segment_path is None:
        print("❌ Failed to encode outro segment")
        sys.exit(1)
    
    print("Step 3: Detecting credits start time...")
    result = detect_outro_start_time_core(
        outro_segment_path=outro_segment_path,
        total_video_duration=total_duration,
        outro_segment_duration=args.duration,
        api_key=args.api_key
    )
    
    if result:
        print("\n✅ Success! Credits start time detection completed:")
        print(f"  Absolute timestamp: {result['timestamp']}")
        print(f"  Relative timestamp in segment: {result['relative_timestamp']}")
        print(f"  Absolute seconds: {result['absolute_seconds']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Cost: ${result['cost']:.6f}")
        print(f"  Tokens used: {result['tokens_used']:,}")
    else:
        print("\n❌ Failed to detect credits start time")
        sys.exit(1)


def test_get_duration(args):
    """Test the video duration detection function."""
    print(f"📏 Testing video duration detection for: {args.video_path}")
    print("-" * 60)
    
    result = get_video_duration_core(video_file_path=args.video_path)
    
    if result is not None:
        hours = result // 3600
        minutes = (result % 3600) // 60
        seconds = result % 60
        
        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"
        
        print("\n✅ Success! Video duration detection completed:")
        print(f"  Duration: {result} seconds")
        print(f"  Human readable: {time_str}")
    else:
        print("\n❌ Failed to detect video duration")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manual testing script for credit-scout functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Encode intro command
    intro_parser = subparsers.add_parser("encode_intro", help="Test intro segment encoding")
    intro_parser.add_argument("video_path", help="Path to the input video file")
    intro_parser.add_argument("--duration", type=float, default=300.0, help="Duration in seconds (default: 300)")
    intro_parser.add_argument("--height", type=int, help="Video height (default: VIDEO_HEIGHT env var or 120)")
    intro_parser.add_argument("--crf", type=int, help="Video CRF quality (default: VIDEO_CRF env var or 28)")
    intro_parser.add_argument("--fps", type=int, help="Video FPS (default: VIDEO_FPS env var or 5)")
    
    # Encode outro command
    outro_parser = subparsers.add_parser("encode_outro", help="Test outro segment encoding")
    outro_parser.add_argument("video_path", help="Path to the input video file")
    outro_parser.add_argument("--duration", type=float, default=600.0, help="Duration in seconds (default: 600)")
    outro_parser.add_argument("--height", type=int, help="Video height (default: VIDEO_HEIGHT env var or 120)")
    outro_parser.add_argument("--crf", type=int, help="Video CRF quality (default: VIDEO_CRF env var or 28)")
    outro_parser.add_argument("--fps", type=int, help="Video FPS (default: VIDEO_FPS env var or 5)")
    
    # Detect intro command
    detect_parser = subparsers.add_parser("detect_intro", help="Test intro end time detection")
    detect_parser.add_argument("video_path", help="Path to the input video file")
    detect_parser.add_argument("--api-key", help="Gemini API key (optional if GEMINI_API_KEY env var is set)")
    
    # Detect outro command
    detect_outro_parser = subparsers.add_parser("detect_outro", help="Test credits start time detection")
    detect_outro_parser.add_argument("video_path", help="Path to the input video file")
    detect_outro_parser.add_argument(
        "--duration", type=float, default=600.0, help="Duration of outro segment in seconds (default: 600)"
    )
    detect_outro_parser.add_argument("--api-key", help="Gemini API key (optional if GEMINI_API_KEY env var is set)")
    
    # Get duration command
    duration_parser = subparsers.add_parser("get_duration", help="Test video duration detection")
    duration_parser.add_argument("video_path", help="Path to the input video file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Validate video file exists
    if not Path(args.video_path).exists():
        print(f"❌ Error: Video file not found: {args.video_path}")
        sys.exit(1)
    
    # Route to appropriate test function
    if args.command == "encode_intro":
        test_encode_intro(args)
    elif args.command == "encode_outro":
        test_encode_outro(args)
    elif args.command == "detect_intro":
        test_detect_intro(args)
    elif args.command == "detect_outro":
        test_detect_outro(args)
    elif args.command == "get_duration":
        test_get_duration(args)


if __name__ == "__main__":
    main() 