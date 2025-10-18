# Video Audio Tools API

A comprehensive API service that provides all audio processing tools from onlineconverter.com, including audio-to-video conversion, speed changes, compression, cutting, extraction, volume control, merging, mixing, noise removal, silence removal, repair, and video audio removal.

## Features

- **URL-based Input**: Accepts audio/video URLs for automatic download
- **Multiple Audio Formats**: Supports MP3, WAV, AAC, M4A, FLAC
- **12 Audio Tools**: Complete suite of audio processing capabilities
- **Docker Containerized**: Ready for deployment
- **Network Integration**: Connected to runtipi_tipi_main_network

## API Endpoints

### 1. Audio to Video Converter

**Endpoint:** `POST /audio-to-video`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "image_url": "https://example.com/image.jpg",  // optional
  "image_color": "Black",  // optional: predefined colors
  "duration": "default",  // "default" or seconds
  "effect": "zoom_in_center",  // optional: supported effects
  "effect_duration": 5.0,
  "effect_enlarge": 1.2
}
```

**Response:** MP4 video file download.

### 2. Change Speed

**Endpoint:** `POST /change-speed`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "speed": 1.5  // 0.5 = half speed, 2.0 = double speed
}
```

**Response:** MP3 audio file with changed speed.

### 3. Compress MP3

**Endpoint:** `POST /compress-mp3`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "bitrate": "128k"  // e.g., "64k", "128k", "192k", "320k"
}
```

**Response:** Compressed MP3 file.

### 4. Cut MP3

**Endpoint:** `POST /cut-mp3`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "start_time": "30",  // start time in seconds
  "duration": "60"     // optional: duration in seconds
}
```

**Response:** Cut MP3 segment.

### 5. Extract Audio

**Endpoint:** `POST /extract-audio`

**Request:**
```json
{
  "video_url": "https://example.com/video.mp4"
}
```

**Response:** MP3 audio extracted from video.

### 6. Change Volume

**Endpoint:** `POST /change-volume`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "volume": 1.5  // 0.0 = mute, 1.0 = original, 2.0 = double volume
}
```

**Response:** MP3 with adjusted volume.

### 7. Merge Audio

**Endpoint:** `POST /merge-audio`

**Request:**
```json
{
  "audio_urls": [
    "https://example.com/audio1.mp3",
    "https://example.com/audio2.mp3"
  ],
  "output_format": "mp3"
}
```

**Response:** Merged audio file.

### 8. Mix Audio

**Endpoint:** `POST /mix-audio`

**Request:**
```json
{
  "audio_urls": [
    "https://example.com/audio1.mp3",
    "https://example.com/audio2.mp3"
  ],
  "volumes": [1.0, 0.5],  // optional: volume for each track
  "output_format": "mp3"
}
```

**Response:** Mixed audio file.

### 9. Remove Audio from Video

**Endpoint:** `POST /remove-audio-from-video`

**Request:**
```json
{
  "video_url": "https://example.com/video.mp4"
}
```

**Response:** Silent MP4 video.

### 10. Remove Noise

**Endpoint:** `POST /remove-noise`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "noise_reduction_level": 0.5
}
```

**Response:** Noise-reduced MP3.

### 11. Remove Silence

**Endpoint:** `POST /remove-silence`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "silence_threshold": -50.0,  // dB threshold
  "silence_duration": 0.5      // minimum silence duration in seconds
}
```

**Response:** MP3 with silence removed.

### 12. Repair M4A

**Endpoint:** `POST /repair-m4a`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.m4a"
}
```

**Response:** Repaired M4A file.

## Supported Options

### Colors (for audio-to-video)
Azure, Black, Blue, Brown, Cyan, Fuchsia, Gold, Gray, Green, Maroon, Navy, Olive, Orange, Pink, Purple, Red, Silver, Skyblue, White, Yellow

### Effects (for audio-to-video)
- `zoom_in_center`: Zoom in to center
- `zoom_out_center`: Zoom out from center
- `pan_left`: Pan from right to left
- `pan_right`: Pan from left to right
- `rotate_left_90`: Rotate 90 degrees left
- `fade_in`: Fade in from black
- `blur_to_clear`: Start blurred, become clear

## API Usage Examples

### Audio to Video
```bash
curl -X POST "http://video-audio-tools:8000/audio-to-video" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "image_color": "Black"}' \
     -o output.mp4
```

### Change Speed
```bash
curl -X POST "http://video-audio-tools:8000/change-speed" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "speed": 1.25}' \
     -o faster.mp3
```

### Compress MP3
```bash
curl -X POST "http://video-audio-tools:8000/compress-mp3" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "bitrate": "128k"}' \
     -o compressed.mp3
```

### Cut MP3
```bash
curl -X POST "http://video-audio-tools:8000/cut-mp3" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "start_time": "30", "duration": "60"}' \
     -o cut_audio.mp3
```

### Extract Audio from Video
```bash
curl -X POST "http://video-audio-tools:8000/extract-audio" \
     -H "Content-Type: application/json" \
     -d '{"video_url": "https://example.com/video.mp4"}' \
     -o extracted.mp3
```

### Change Volume
```bash
curl -X POST "http://video-audio-tools:8000/change-volume" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "volume": 1.5}' \
     -o louder.mp3
```

### Merge Audio
```bash
curl -X POST "http://video-audio-tools:8000/merge-audio" \
     -H "Content-Type: application/json" \
     -d '{"audio_urls": ["https://example.com/audio1.mp3", "https://example.com/audio2.mp3"], "output_format": "mp3"}' \
     -o merged.mp3
```

### Mix Audio
```bash
curl -X POST "http://video-audio-tools:8000/mix-audio" \
     -H "Content-Type: application/json" \
     -d '{"audio_urls": ["https://example.com/audio1.mp3", "https://example.com/audio2.mp3"], "volumes": [1.0, 0.5], "output_format": "mp3"}' \
     -o mixed.mp3
```

### Remove Audio from Video
```bash
curl -X POST "http://video-audio-tools:8000/remove-audio-from-video" \
     -H "Content-Type: application/json" \
     -d '{"video_url": "https://example.com/video.mp4"}' \
     -o silent_video.mp4
```

### Remove Noise
```bash
curl -X POST "http://video-audio-tools:8000/remove-noise" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "noise_reduction_level": 0.5}' \
     -o denoised.mp3
```

### Remove Silence
```bash
curl -X POST "http://video-audio-tools:8000/remove-silence" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "silence_threshold": -50.0, "silence_duration": 0.5}' \
     -o no_silence.mp3
```

### Repair M4A
```bash
curl -X POST "http://video-audio-tools:8000/repair-m4a" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.m4a"}' \
     -o repaired.m4a
```

### Probe Media
```bash
curl -X POST "http://video-audio-tools:8000/probe-media" \
     -H "Content-Type: application/json" \
     -d '{"media_url": "https://example.com/audio.mp3"}'
```

### Get Duration
```bash
curl -X POST "http://video-audio-tools:8000/get-duration" \
     -H "Content-Type: application/json" \
     -d '{"media_url": "https://example.com/audio.mp3"}'
```

### Get Thumbnail
```bash
curl -X POST "http://video-audio-tools:8000/get-thumbnail" \
     -H "Content-Type: application/json" \
     -d '{"video_url": "https://example.com/video.mp4", "timestamp": "00:00:05", "width": 320, "height": 240}' \
     -o thumbnail.jpg
```

### Get Waveform
```bash
curl -X POST "http://video-audio-tools:8000/get-waveform" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "width": 800, "height": 200, "color": "blue"}' \
     -o waveform.png
```

### Get Audio Info
```bash
curl -X POST "http://video-audio-tools:8000/get-audio-info" \
     -H "Content-Type: application/json" \
     -d '{"media_url": "https://example.com/audio.mp3"}'
```

### Get Video Info
```bash
curl -X POST "http://video-audio-tools:8000/get-video-info" \
     -H "Content-Type: application/json" \
     -d '{"media_url": "https://example.com/video.mp4"}'
```

### Health Check
```bash
curl "http://video-audio-tools:8000/health"
```

### API Info
```bash
curl "http://video-audio-tools:8000/"
```

## Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "video-audio-tools"
}
```

## API Info

**Endpoint:** `GET /`

**Response:** Complete API documentation with all available tools.

## Media Analysis & Probe Tools

### 13. Probe Media

**Endpoint:** `POST /probe-media`

**Request:**
```json
{
  "media_url": "https://example.com/audio.mp3"
}
```

**Response:** Comprehensive media file information including format, duration, streams, codecs, and metadata.

### 14. Get Duration

**Endpoint:** `POST /get-duration`

**Request:**
```json
{
  "media_url": "https://example.com/audio.mp3"
}
```

**Response:**
```json
{
  "duration_seconds": 123.456,
  "duration_formatted": "00:02:03.456",
  "hours": 0,
  "minutes": 2,
  "seconds": 3,
  "milliseconds": 456
}
```

### 15. Get Thumbnail

**Endpoint:** `POST /get-thumbnail`

**Request:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "timestamp": "00:00:05",
  "width": 320,
  "height": 240
}
```

**Response:** JPEG thumbnail image from the specified timestamp.

### 16. Get Waveform

**Endpoint:** `POST /get-waveform`

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "width": 800,
  "height": 200,
  "color": "blue"
}
```

**Response:** PNG waveform visualization image.

### 17. Get Audio Info

**Endpoint:** `POST /get-audio-info`

**Request:**
```json
{
  "media_url": "https://example.com/audio.mp3"
}
```

**Response:** Detailed audio file information including codec, channels, sample rate, bitrate, and tags.

### 18. Get Video Info

**Endpoint:** `POST /get-video-info`

**Request:**
```json
{
  "media_url": "https://example.com/video.mp4"
}
```

**Response:** Detailed video file information including resolution, FPS, codec, aspect ratio, and metadata.

## Running

1. Build and run with Docker Compose:
```bash
docker-compose up --build -d
```

2. The API will be available at `http://video-audio-tools:8000` within the runtipi_tipi_main_network.

## Requirements

- Docker
- Docker Compose
- FFmpeg (included in container)
- ImageMagick (included in container)