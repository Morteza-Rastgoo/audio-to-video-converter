# GitHub Copilot Instructions for Video Audio Tools API

## Project Overview
This is a FastAPI-based microservice for comprehensive audio and video processing tools. The API provides 18+ endpoints for various media processing operations including audio-to-video conversion, speed changes, compression, cutting, extraction, volume control, merging, mixing, noise reduction, silence removal, and video effects.

## Code Structure
- `app.py`: Main FastAPI application with all endpoints
- `requirements.txt`: Python dependencies
- `Dockerfile`: Containerization setup
- `docker-compose.yml`: Local development environment
- `README.md`: API documentation and usage examples

## API Design Patterns

### Endpoint Naming
- Use kebab-case for endpoint paths: `/audio-to-video`, `/change-speed`
- Use camelCase for Python function names: `audio_to_video`, `change_speed`

### Request/Response Models
- Define Pydantic models for all request/response data
- Use descriptive field names with proper types
- Include optional fields with `Optional[Type] = None`

### Error Handling
- Use `HTTPException` for API errors with appropriate status codes
- Provide meaningful error messages
- Handle exceptions gracefully with try/catch blocks

### File Processing
- Use `tempfile.mkdtemp()` for temporary directories
- Always clean up temporary files in try/finally blocks
- Download files using `requests.get()` with proper error handling
- Return files using `FileResponse` with correct media types

## FFmpeg Usage Guidelines

### Command Construction
- Build FFmpeg commands as lists, not strings: `["ffmpeg", "-i", input_path, ...]`
- Use `subprocess.run()` with `check=True` and `capture_output=True`
- Always specify output files explicitly with `-y` flag for overwriting

### Filter Complex
- Use `-filter_complex` for complex video filters
- Escape special characters properly in filter strings
- Test filters manually before implementing

### Audio/Video Codecs
- Default to `libx264` for video encoding
- Default to `aac` for audio encoding
- Use `libmp3lame` for MP3 output
- Set appropriate bitrates: `-b:a 192k` for audio, `-b:v 1M` for video

## Testing and Validation

### Manual Testing
- Test all endpoints with real URLs before committing
- Verify output file formats and sizes
- Check that temporary files are cleaned up

### Error Scenarios
- Test with invalid URLs (should return 400)
- Test with unsupported file formats
- Test with very large files (consider size limits)

## Development Workflow

### Code Changes
- Always test changes locally with Docker: `docker compose up --build`
- Update README.md with new endpoint examples
- Add new Pydantic models for new request types

### Git Practices
- Use descriptive commit messages
- Test before pushing to avoid breaking the API
- Keep the repository clean (no test files committed)

## Common Patterns

### File Download
```python
def download_file(url: str, temp_dir: str, filename: str = None) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download file")
    # ... rest of implementation
```

### FFmpeg Processing
```python
cmd = ["ffmpeg", "-i", input_path, "-filter:a", filter_expression, "-c:a", "libmp3lame", "-y", output_path]
subprocess.run(cmd, check=True, capture_output=True)
```

### API Response
```python
return FileResponse(output_path, media_type='audio/mpeg', filename="processed.mp3")
```

## Quality Standards

### Code Quality
- Use type hints for all function parameters and return values
- Write descriptive docstrings for complex functions
- Keep functions focused on single responsibilities

### API Consistency
- Maintain consistent parameter naming across endpoints
- Use standard HTTP status codes
- Provide helpful error messages

### Performance
- Process files in memory when possible
- Clean up temporary files immediately after use
- Consider file size limits for large uploads

## Deployment
- Use Docker for consistent environments
- Expose port 8085 in docker-compose.yml
- Mount volumes if needed for persistent storage

## Security Considerations
- Validate all input URLs and file types
- Limit file sizes to prevent abuse
- Use secure temporary file creation
- Avoid shell injection in FFmpeg commands (use list format)

## Troubleshooting
- Check Docker logs: `docker compose logs`
- Test FFmpeg commands manually before implementing
- Verify network connectivity for external URLs
- Check file permissions in containers