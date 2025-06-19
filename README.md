# Credit Scout: AI-Powered Movie Intro/Outro Detection

![Credit Scout Banner](./cover.jpg)

[![GitHub stars](https://img.shields.io/github/stars/patrickkalkman/credit-scout)](https://github.com/PatrickKalkman/credit-scout/stargazers)
[![GitHub contributors](https://img.shields.io/github/contributors/patrickkalkman/credit-scout)](https://github.com/PatrickKalkman/credit-scout/graphs/contributors)
[![GitHub last commit](https://img.shields.io/github/last-commit/patrickkalkman/credit-scout)](https://github.com/PatrickKalkman/credit-scout)
[![open issues](https://img.shields.io/github/issues/patrickkalkman/credit-scout)](https://github.com/PatrickKalkman/credit-scout/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Credit Scout detects movie intro end and outro start timestamps using multimodal AI, for just $0.30 per movie instead of $6 with traditional APIs. See this Medium article for more details: [Detecting Movie Intros and Outros with AI](https://medium.com/ai-advances/skip-intro-at-scale-how-i-built-netflixs-missing-feature-for-0-30-per-movie-12ef196bc3d8).

## ✨ Features

- 🎬 **Automated Detection**: Uses AI to identify when the actual movie begins and credits end
- 💰 **20× Cost Reduction**: ~$0.30 per movie vs $6 with Amazon Rekognition
- ⚡ **Smart Sampling**: Analyzes strategic segments instead of entire videos
- 🤖 **Multimodal AI**: Combines GPT-4o mini orchestration with Gemini 2.5 Pro vision
- 📊 **Cost Tracking**: Monitors API usage and provides detailed cost breakdowns
- 🛠️ **CLI Interface**: Simple command-line usage with beautiful terminal output
- 🎯 **High Accuracy**: Tested on diverse content with consistent results

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** with uv package manager
- **FFmpeg** installed and accessible in PATH
- **OpenAI API Key** (for agent orchestration)
- **Google Gemini API Key** (for video analysis)

### System Requirements

- **OS**: Linux, macOS, or Windows 10/11
- **RAM**: 4GB available (video processing can be memory-intensive)
- **Storage**: 2GB free space for temporary files
- **CPU**: Multi-core recommended for faster encoding
- **Network**: Stable internet connection for API calls

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/patrickkalkman/credit-scout.git
cd credit-scout
```

2. **Install FFmpeg**:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

3. **Install UV** (if not already installed):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

4. **Create `.env` file**:
```bash
# Create .env file in project root
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Customize video processing settings
VIDEO_HEIGHT=120  # Lower = faster, higher = more accurate
VIDEO_CRF=28     # Quality: lower = better, higher = smaller file
VIDEO_FPS=5      # Frame rate: lower = faster processing
```

### Getting API Keys

- **OpenAI API Key**: 
  - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Required model: GPT-4o mini
  - Cost: ~$0.001 per film

- **Google Gemini API Key**: 
  - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
  - Required model: Gemini 2.5 Pro Preview
  - Cost: ~$0.297 per film

## 🔧 Usage

### Command Line Interface

```bash
# Run Credit Scout on a movie
uv run run.py ./your-movie.mp4

# The tool will output timestamps like:
# ┌─────────────────────────────────────────────────────────────┐
# │                     Analysis Results                        │
# ├─────────────────────────────────────────────────────────────┤
# │ Intro ends at: 01:10                                       │
# │ Outro starts at: 87:42                                     │
# │ Total analysis cost: $0.297                                │
# │ Analysis timestamp: 2025-05-25T12:49:02                    │
# └─────────────────────────────────────────────────────────────┘
```

### Output Format

Credit Scout saves results as JSON files:

```json
{
  "intro_end_time": "01:10",
  "outro_start_time": "09:50",
  "total_cost": 0.297,
  "analysis_timestamp": "2025-05-25T12:49:02.741502",
  "video_file": {
    "name": "tears_of_steel.mp4",
    "path": "/path/to/movie.mp4"
  }
}
```

## 💡 How It Works

Credit Scout uses a strategic approach to minimize costs while maintaining accuracy:

1. **Video Preprocessing**: Converts segments to grayscale 120p at 5fps
2. **Strategic Sampling**: 
   - Analyzes first 5 minutes for intro detection
   - Analyzes last 10 minutes for outro detection
3. **Multimodal Analysis**: 
   - GPT-4o mini orchestrates the workflow
   - Gemini 2.5 Pro analyzes video frames
4. **Intelligent Detection**: Recognizes studio logos, title cards, and credit sequences

## 📊 Benchmark Results

Tested on 10 open-source films with 100% success rate:

| Movie | Intro End | Outro Start | Cost | Time |
|-------|-----------|-------------|------|------|
| Tears of Steel | 01:10 | 09:50 | $0.297 | ~101s |
| Sintel | 01:43 | 12:27 | $0.297 | ~130s |
| Big Buck Bunny | 00:10 | 09:18 | $0.297 | ~90s |
| Cosmos Laundromat | 00:59 | 10:10 | $0.297 | ~98s |

**Average cost per movie: $0.23**
## 🔌 Architecture

- **OpenAI Agents SDK**: Orchestration layer for coordinating tools
- **Google Gemini 2.5 Pro**: Visual understanding and content analysis
- **FFmpeg**: Video processing and segment extraction
- **Smart Sampling**: Processes only ~15 minutes of content per movie

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest tests/

# Format code
uv run ruff format .
uv run ruff check .
```

## 📝 Roadmap

- [ ] Push resolution boundaries (test 60p, 2fps)
- [ ] Local LLM support for privacy
- [ ] TV episode support with mid-roll detection
- [ ] Scene transition detection
- [ ] Batch processing for libraries

## 🙏 Acknowledgments

- Built with [OpenAI Agents SDK](https://github.com/openai/openai-python) for orchestration
- Uses [Google Gemini](https://ai.google.dev/) for visual analysis
- [FFmpeg](https://ffmpeg.org/) for video processing
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Tested on [Blender Foundation](https://studio.blender.org/) open-source films

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ by Patrick Kalkman. Star the repo if you find it useful!