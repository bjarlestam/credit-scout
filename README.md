# Credit Scout

AI agent for movie credit detection using OpenAI Agents SDK and Google Gemini.

## Overview

Credit Scout is an intelligent movie analysis tool that automatically detects:
- **Intro End Time**: When the main movie content begins (after logos, titles, opening credits)
- **Outro Start Time**: When the end credits begin

The agent uses a combination of video processing and AI analysis to provide accurate timestamps.

## Features

- 🎬 **Automated Analysis**: Uses AI to analyze video content and detect transitions
- ⚡ **Optimized Processing**: Encodes low-resolution segments for faster analysis
- 💰 **Cost Tracking**: Monitors API usage and costs
- 🛠️ **CLI Interface**: Easy-to-use command-line interface
- 📊 **Rich Output**: Beautiful terminal output with progress indicators

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd credit-scout
```

2. Install dependencies:
```bash
pip install -e .
```

3. Install FFmpeg (required for video processing):
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Configuration

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit `.env` and add your API keys:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Video Processing Settings (optional)
VIDEO_HEIGHT=120
VIDEO_FPS=5
VIDEO_CRF=28
```

### Getting API Keys

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Usage

### Command Line Interface

```bash
# Method 1: Using the installed command (after pip install -e .)
credit-scout /path/to/movie.mp4

# Method 2: Using the run script from project root
python run_credit_scout.py /path/to/movie.mp4

# Method 3: Using uv run with the run script
uv run run_credit_scout.py /path/to/movie.mp4

# Method 4: Using Python module (if installed)
python -m credit_scout.main /path/to/movie.mp4
```

### Programmatic Usage

```python
import asyncio
from credit_scout.movie_analysis_agent import analyze_movie

async def main():
    result = await analyze_movie("/path/to/movie.mp4")
    print(result)

asyncio.run(main())
```

### Example Output

```
┌─────────────────────────────────────────────────────────────┐
│                     Analysis Results                        │
├─────────────────────────────────────────────────────────────┤
│ Intro ends at: 02:15                                       │
│ Outro starts at: 87:42                                     │
│ Total analysis cost: $0.045                                │
│ Confidence: High                                            │
└─────────────────────────────────────────────────────────────┘
```

## How It Works

The agent follows a sophisticated workflow:

1. **Video Duration Analysis**: Determines total movie length using FFmpeg
2. **Intro Analysis**: 
   - Analyzes the full video file for maximum accuracy
   - Detects when main content begins after logos and titles
3. **Outro Analysis**:
   - Encodes a low-resolution segment from the end of the movie
   - Detects when end credits begin
   - Returns absolute timestamps in the full video

## Architecture

- **Agent Framework**: Built on OpenAI Agents SDK
- **Video Analysis**: Google Gemini 2.5 Pro for visual content analysis
- **Video Processing**: FFmpeg for encoding and duration detection
- **Tools Available**:
  - `get_video_duration`: Get total video duration
  - `encode_intro_segment`: Create optimized intro segment
  - `encode_outro_segment`: Create optimized outro segment  
  - `detect_intro_end_time`: AI analysis of intro end
  - `detect_outro_start_time`: AI analysis of outro start

## Supported Formats

- MP4, AVI, MKV, MOV, WMV
- Any format supported by FFmpeg

## Cost Considerations

- Intro analysis: ~$0.02-0.05 per movie (full video analysis)
- Outro analysis: ~$0.01-0.03 per movie (segment analysis)
- Total cost typically under $0.10 per movie

## Troubleshooting

### Common Issues

1. **FFmpeg not found**:
   ```bash
   # Verify FFmpeg installation
   ffmpeg -version
   ```

2. **API key errors**:
   - Ensure keys are set in `.env` file
   - Check key validity and quotas

3. **Video format issues**:
   - Try converting to MP4 format
   - Ensure video file is not corrupted

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
ruff format .
ruff check .
```

## License

MIT License - see LICENSE file for details.
