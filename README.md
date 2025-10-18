# Audio to Video Converter

A comprehensive API service that converts audio files to video files with advanced features, similar to online converters.

## Features

- **URL-based Input**: Accepts audio URLs for automatic download
- **Multiple Audio Formats**: Supports MP3, WAV, AAC, M4A, FLAC
- **Flexible Backgrounds**: 
  - Custom image URLs
  - 20 predefined solid colors
  - Automatic album art extraction
- **Duration Control**: Default (full audio) or fixed duration (1-300 seconds)
- **Video Effects**: 7 built-in effects (zoom, pan, rotate, fade, blur)
- **Docker Containerized**: Ready for deployment
- **Network Integration**: Connected to runtipi_tipi_main_network

## API Endpoints

### Convert Audio to Video

**Endpoint:** `POST /convert`

**Request:** JSON body with options

```json
{
  "audio_url": "https://example.com/audio.mp3",
  "image_url": "https://example.com/image.jpg",  // optional
  "image_color": "Black",  // optional: predefined colors
  "duration": "default",  // "default" or seconds
  "effect": "zoom_in_center",  // optional: supported effects
  "effect_duration": 5.0,
  "effect_enlarge": 1.2,
  "effect_background": "default"
}
```

**Response:** MP4 video file download.

### Health Check

**Endpoint:** `GET /health`

**Response:** Service status

### API Info

**Endpoint:** `GET /`

**Response:** API documentation and supported options

## API Usage

### Convert Audio to Video

**Endpoint:** `POST /convert`

**Request:** JSON body with options

```json
{
  "audio_url": "https://example.com/audio.mp3",
  "image_url": "https://example.com/image.jpg",  // optional
  "image_color": "Black",  // optional: Azure, Black, Blue, Brown, Cyan, Fuchsia, Gold, Gray, Green, Maroon, Navy, Olive, Orange, Pink, Purple, Red, Silver, Skyblue, White, Yellow
  "duration": "default",  // "default" or seconds like "10"
  "effect": "zoom_in_center",  // optional: zoom_in_center, pan_left, etc.
  "effect_duration": 5.0,
  "effect_enlarge": 1.2,
  "effect_background": "default"
}
```

**Response:** MP4 video file download.

Example using curl:
```bash
curl -X POST "http://audio-to-video:8000/convert" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3", "image_color": "Black", "duration": "10"}' \
     -o output.mp4
```

Options:
- `image_url`: Custom background image URL
- `image_color`: Solid color background (takes precedence over image_url and album art)
- `duration`: "default" for full audio length, or fixed seconds
- `effect`: Video effect to apply. Supported effects:
  - `zoom_in_center`: Zoom in to center
  - `zoom_out_center`: Zoom out from center  
  - `pan_left`: Pan image from right to left
  - `pan_right`: Pan image from left to right
  - `rotate_left_90`: Rotate 90 degrees left
  - `fade_in`: Fade in from black
  - `blur_to_clear`: Start blurred, become clear

## Running

1. Build and run with Docker Compose:
```bash
docker-compose up --build -d
```

2. The API will be available at `http://audio-to-video:8000` within the runtipi_tipi_main_network.

## Requirements

- Docker
- Docker Compose
- External Docker network named `runtipi_tipi_main_network`