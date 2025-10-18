import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import subprocess
import tempfile
import shutil
import requests
from pydantic import BaseModel

app = FastAPI(title="Audio to Video Converter", description="Convert audio files to video with background image")

class ConvertRequest(BaseModel):
    audio_url: str
    image_url: str = None

@app.post("/convert")
async def convert_audio_to_video(request: ConvertRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        # Download audio file
        audio_response = requests.get(request.audio_url)
        if audio_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download audio file")
        
        audio_path = os.path.join(temp_dir, "audio.mp3")  # Assume mp3 for now
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
        
        # Determine image path
        image_path = "/app/default.jpg"  # Default
        if request.image_url:
            # Download custom image
            image_response = requests.get(request.image_url)
            if image_response.status_code == 200:
                image_path = os.path.join(temp_dir, "custom_image.jpg")
                with open(image_path, "wb") as f:
                    f.write(image_response.content)
        else:
            # Try to extract album art from audio
            extracted_image = os.path.join(temp_dir, "extracted.jpg")
            cmd_extract = [
                "ffmpeg",
                "-i", audio_path,
                "-an",  # No audio
                "-vcodec", "copy",
                "-y",
                extracted_image
            ]
            try:
                subprocess.run(cmd_extract, check=True, capture_output=True)
                if os.path.exists(extracted_image):
                    image_path = extracted_image
            except subprocess.CalledProcessError:
                pass  # Use default
        
        # Output video path
        output_path = os.path.join(temp_dir, "output.mp4")
        
        # FFmpeg command to create video from image and audio
        cmd = [
            "ffmpeg",
            "-loop", "1",           # Loop the image
            "-i", image_path,       # Input image
            "-i", audio_path,       # Input audio
            "-map", "0:v",          # Map video from first input (image)
            "-map", "1:a",          # Map audio from second input (audio)
            "-c:v", "libx264",      # Video codec
            "-tune", "stillimage",  # Optimize for still image
            "-c:a", "aac",          # Audio codec
            "-b:a", "192k",         # Audio bitrate
            "-pix_fmt", "yuv420p",  # Pixel format for compatibility
            "-shortest",            # End when shortest input ends
            "-y",                   # Overwrite output
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Conversion failed: {e.stderr}")
        
        # Return the converted video file
        return FileResponse(
            output_path, 
            media_type='video/mp4', 
            filename="converted.mp4"
        )
    finally:
        # Note: temp dir not cleaned for response sending
        pass

@app.get("/")
async def root():
    return {"message": "Audio to Video Converter API", "endpoint": "/convert (POST with JSON: {'audio_url': '...', 'image_url': '...'})"}