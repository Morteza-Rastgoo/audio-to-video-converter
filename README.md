# Audio to Video Converter

A simple API service that converts audio files to video files by combining them with a background image.

## Features

- Accepts audio URLs for download and conversion
- Optional custom image URL for background
- Automatically extracts album art from audio files if no image provided
- Converts to MP4 video with H.264 video and AAC audio
- Docker containerized
- Connected to runtipi_tipi_main_network

## API Usage

### Convert Audio to Video

**Endpoint:** `POST /convert`

**Request:** JSON body with URLs

```json
{
  "audio_url": "https://example.com/audio.mp3",
  "image_url": "https://example.com/image.jpg"  // optional
}
```

**Response:** MP4 video file download.

Example using curl:
```bash
curl -X POST "http://audio-to-video:8000/convert" \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/audio.mp3"}' \
     -o output.mp4
```

If `image_url` is not provided, the API will attempt to use album art from the audio file.

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