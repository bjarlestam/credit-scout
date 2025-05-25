# Test Data Directory

This directory contains test video files used for integration testing of the video encoding functions.

## Setup Instructions

To run the full integration tests, you need to provide sample video files in this directory.

### Required Files

- `sample_video.mp4` - A sample video file for testing both intro and outro segment encoding

### Recommended Video Characteristics

- **Duration**: At least 30 seconds (to test both intro and outro segments)
- **Format**: MP4 with H.264 video codec
- **Resolution**: Any resolution (will be scaled down during testing)
- **File Size**: Keep under 50MB for faster test execution
- **Content**: Any content is fine - the tests focus on technical encoding functionality

### Example Setup

```bash
# Create a test video using ffmpeg (if you have it installed)
ffmpeg -f lavfi -i testsrc=duration=60:size=640x480:rate=30 -c:v libx264 -t 60 tests/test_data/sample_video.mp4

# Or copy an existing video file
cp /path/to/your/video.mp4 tests/test_data/sample_video.mp4
```

### Running Tests

```bash
# Run all tests (unit tests will run even without video files)
uv run pytest tests/

# Run only unit tests (skip integration tests)
uv run pytest tests/ -m "not integration"

# Run only integration tests (requires video files)
uv run pytest tests/ -m "integration"

# Run with verbose output
uv run pytest tests/ -v
```

### Test Behavior

- **Without video files**: Unit tests will run normally, integration tests will be skipped
- **With video files**: All tests will run, including actual video encoding tests
- **Test cleanup**: Temporary files created during testing are automatically cleaned up

### Security Note

Do not commit actual video files to the repository. This directory should contain only test files for local development and CI environments should use generated test content. 