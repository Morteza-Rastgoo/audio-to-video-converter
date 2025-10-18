import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import subprocess
import tempfile
import shutil
import requests
from pydantic import BaseModel

app = FastAPI(title="Audio to Video Converter", description="Convert audio files to video with background image")

from pydantic import BaseModel

class ConvertRequest(BaseModel):
    audio_url: str
    image_url: str = None
    image_color: str = None  # e.g., "Black", "White", "Red", etc.
    duration: str = "default"  # "default" or number like "10"
    effect: str = None  # e.g., "zoom_in_center", "pan_left", etc.
    effect_duration: float = 5.0
    effect_enlarge: float = 1.2
    effect_background: str = "default"

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
        if request.image_color:
            # Generate solid color image
            color_map = {
                "azure": "#f0ffff", "black": "#000000", "blue": "#0000ff", "brown": "#a52a2a",
                "cyan": "#00ffff", "fuchsia": "#ff00ff", "gold": "#ffd700", "gray": "#808080",
                "green": "#008000", "maroon": "#800000", "navy": "#000080", "olive": "#808000",
                "orange": "#ffa500", "pink": "#ffc0cb", "purple": "#800080", "red": "#ff0000",
                "silver": "#c0c0c0", "skyblue": "#87ceeb", "white": "#ffffff", "yellow": "#ffff00"
            }
            color = color_map.get(request.image_color.lower(), "#000000")
            image_path = os.path.join(temp_dir, "color_image.jpg")
            # Use ImageMagick to create color image
            subprocess.run(["convert", "-size", "1920x1080", f"xc:{color}", image_path], check=True)
        elif request.image_url:
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
        
        # Build FFmpeg command
        cmd = ["ffmpeg", "-loop", "1", "-i", image_path, "-i", audio_path]
        
        # Add duration if specified
        if request.duration != "default":
            try:
                dur = float(request.duration)
                cmd.extend(["-t", str(dur)])
            except ValueError:
                pass  # Ignore invalid duration
        
        # Add effect if specified
        filter_complex = None
        if request.effect:
            if request.effect == "zoom_in_center":
                # Simple zoom in
                filter_complex = f"zoompan=z='min(max(zoom,pzoom)+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080"
            elif request.effect == "pan_left":
                filter_complex = "crop=1920:1080:0:0"  # Placeholder, pan would need more complex
            # Add more effects as needed
        
        if filter_complex:
            cmd.extend(["-filter_complex", filter_complex])
        
        cmd.extend([
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-shortest", "-y", output_path
        ])
        
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