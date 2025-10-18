import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import subprocess
import tempfile
import requests
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Universal Audio Tools API", description="Comprehensive audio processing tools")

# Pydantic models
class AudioToVideoRequest(BaseModel):
    audio_url: str
    image_url: Optional[str] = None
    image_color: Optional[str] = None
    duration: str = "default"
    effect: Optional[str] = None
    effect_duration: float = 5.0
    effect_enlarge: float = 1.2

class SpeedChangeRequest(BaseModel):
    audio_url: str
    speed: float = 1.0

class CompressRequest(BaseModel):
    audio_url: str
    bitrate: str = "128k"

class CutRequest(BaseModel):
    audio_url: str
    start_time: str = "0"
    duration: Optional[str] = None

class VolumeChangeRequest(BaseModel):
    audio_url: str
    volume: float = 1.0

class MergeRequest(BaseModel):
    audio_urls: List[str]
    output_format: str = "mp3"

class MixRequest(BaseModel):
    audio_urls: List[str]
    volumes: Optional[List[float]] = None
    output_format: str = "mp3"

class VideoAudioRequest(BaseModel):
    video_url: str

class NoiseReductionRequest(BaseModel):
    audio_url: str
    noise_reduction_level: float = 0.5

class SilenceRemovalRequest(BaseModel):
    audio_url: str
    silence_threshold: float = -50.0
    silence_duration: float = 0.5

class RepairRequest(BaseModel):
    audio_url: str

# Utility functions
def download_file(url: str, temp_dir: str, filename: str = None) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download file")
    
    if not filename:
        filename = url.split('/')[-1] or "file"
    
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path

# Endpoints
@app.post("/audio-to-video")
async def audio_to_video(request: AudioToVideoRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "audio.mp3")
        
        image_path = "/app/default.jpg"
        if request.image_color:
            color_map = {
                "azure": "#f0ffff", "black": "#000000", "blue": "#0000ff", "brown": "#a52a2a",
                "cyan": "#00ffff", "fuchsia": "#ff00ff", "gold": "#ffd700", "gray": "#808080",
                "green": "#008000", "maroon": "#800000", "navy": "#000080", "olive": "#808000",
                "orange": "#ffa500", "pink": "#ffc0cb", "purple": "#800080", "red": "#ff0000",
                "silver": "#c0c0c0", "skyblue": "#87ceeb", "white": "#ffffff", "yellow": "#ffff00"
            }
            color = color_map.get(request.image_color.lower(), "#000000")
            image_path = os.path.join(temp_dir, "color.jpg")
            subprocess.run(["convert", "-size", "1920x1080", f"xc:{color}", image_path], check=True)
        elif request.image_url:
            image_path = download_file(request.image_url, temp_dir, "image.jpg")
        else:
            extracted = os.path.join(temp_dir, "extracted.jpg")
            try:
                subprocess.run(["ffmpeg", "-i", audio_path, "-an", "-vcodec", "copy", "-y", extracted], check=True, capture_output=True)
                if os.path.exists(extracted):
                    image_path = extracted
            except:
                pass
        
        cmd = ["ffmpeg", "-loop", "1", "-i", image_path, "-i", audio_path]
        
        if request.duration != "default":
            cmd.extend(["-t", request.duration])
        
        filter_complex = None
        if request.effect == "zoom_in_center":
            filter_complex = f"zoompan=z='min(max(zoom,pzoom)+0.0015,{request.effect_enlarge})':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080"
        elif request.effect == "zoom_out_center":
            filter_complex = f"zoompan=z='max(min(zoom,pzoom)-0.0015,1/{request.effect_enlarge})':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080"
        elif request.effect == "pan_left":
            filter_complex = "crop=1920:1080:(1920-1920*progress):0,scale=1920:1080"
        elif request.effect == "pan_right":
            filter_complex = "crop=1920:1080:(0-1920*progress):0,scale=1920:1080"
        elif request.effect == "rotate_left_90":
            filter_complex = "rotate=PI/2:ow=1920:oh=1080:c=black@0"
        elif request.effect == "fade_in":
            filter_complex = "fade=t=in:st=0:d=2:alpha=1"
        elif request.effect == "blur_to_clear":
            filter_complex = "boxblur=10:enable='lt(t,0.5)',boxblur=0:enable='gte(t,0.5)'"
        
        if filter_complex:
            cmd.extend(["-filter_complex", filter_complex])
        
        output_path = os.path.join(temp_dir, "output.mp4")
        cmd.extend(["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", "-y", output_path])
        
        subprocess.run(cmd, check=True, capture_output=True)
        return FileResponse(output_path, media_type='video/mp4', filename="video.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change-speed")
async def change_speed(request: SpeedChangeRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "input.mp3")
        output_path = os.path.join(temp_dir, "output.mp3")
        
        cmd = ["ffmpeg", "-i", audio_path, "-filter:a", f"atempo={request.speed}", "-c:a", "libmp3lame", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="speed_changed.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compress-mp3")
async def compress_mp3(request: CompressRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "input.mp3")
        output_path = os.path.join(temp_dir, "output.mp3")
        
        cmd = ["ffmpeg", "-i", audio_path, "-c:a", "libmp3lame", "-b:a", request.bitrate, "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="compressed.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cut-mp3")
async def cut_mp3(request: CutRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "input.mp3")
        output_path = os.path.join(temp_dir, "output.mp3")
        
        cmd = ["ffmpeg", "-i", audio_path, "-ss", request.start_time]
        if request.duration:
            cmd.extend(["-t", request.duration])
        cmd.extend(["-c", "copy", "-y", output_path])
        
        subprocess.run(cmd, check=True, capture_output=True)
        return FileResponse(output_path, media_type='audio/mpeg', filename="cut.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-audio")
async def extract_audio(request: VideoAudioRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        video_path = download_file(request.video_url, temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp3")
        
        cmd = ["ffmpeg", "-i", video_path, "-vn", "-c:a", "libmp3lame", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="audio.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change-volume")
async def change_volume(request: VolumeChangeRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "input.mp3")
        output_path = os.path.join(temp_dir, "output.mp3")
        
        cmd = ["ffmpeg", "-i", audio_path, "-filter:a", f"volume={request.volume}", "-c:a", "libmp3lame", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="volume_changed.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/merge-audio")
async def merge_audio(request: MergeRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_paths = [download_file(url, temp_dir, f"input_{i}.mp3") for i, url in enumerate(request.audio_urls)]
        
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, "w") as f:
            for path in audio_paths:
                f.write(f"file '{path}'\n")
        
        output_path = os.path.join(temp_dir, f"output.{request.output_format}")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="merged.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mix-audio")
async def mix_audio(request: MixRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_paths = [download_file(url, temp_dir, f"input_{i}.mp3") for i, url in enumerate(request.audio_urls)]
        
        inputs = []
        for path in audio_paths:
            inputs.extend(["-i", path])
        
        volumes = request.volumes or [1.0] * len(audio_paths)
        filter_parts = [f"[{i}:a]volume={volumes[i]}[a{i}]" for i in range(len(audio_paths))]
        filter_parts.append(f"{' '.join([f'[a{i}]' for i in range(len(audio_paths))])}amix=inputs={len(audio_paths)}[out]")
        filter_complex = ','.join(filter_parts)
        
        output_path = os.path.join(temp_dir, f"output.{request.output_format}")
        cmd = ["ffmpeg"] + inputs + ["-filter_complex", filter_complex, "-map", "[out]", "-c:a", "libmp3lame", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="mixed.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/remove-audio-from-video")
async def remove_audio_from_video(request: VideoAudioRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        video_path = download_file(request.video_url, temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp4")
        
        cmd = ["ffmpeg", "-i", video_path, "-c:v", "copy", "-an", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='video/mp4', filename="silent.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/remove-noise")
async def remove_noise(request: NoiseReductionRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "input.mp3")
        output_path = os.path.join(temp_dir, "output.mp3")
        
        cmd = ["ffmpeg", "-i", audio_path, "-filter:a", "highpass=f=80,lowpass=f=8000,compand=attacks=0.3:decays=0.8:points=-70/-60|-30/-10", "-c:a", "libmp3lame", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="noise_reduced.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/remove-silence")
async def remove_silence(request: SilenceRemovalRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "input.mp3")
        output_path = os.path.join(temp_dir, "output.mp3")
        
        cmd = ["ffmpeg", "-i", audio_path, "-filter:a", f"silenceremove=stop_periods=-1:stop_duration={request.silence_duration}:stop_threshold={request.silence_threshold}dB", "-c:a", "libmp3lame", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mpeg', filename="silence_removed.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repair-m4a")
async def repair_m4a(request: RepairRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "input.m4a")
        output_path = os.path.join(temp_dir, "output.m4a")
        
        cmd = ["ffmpeg", "-i", audio_path, "-c:a", "aac", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return FileResponse(output_path, media_type='audio/mp4', filename="repaired.m4a")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "universal-audio-tools"}

@app.get("/")
async def root():
    return {
        "message": "Universal Audio Tools API",
        "version": "3.0",
        "tools": [
            "audio-to-video", "change-speed", "compress-mp3", "cut-mp3",
            "extract-audio", "change-volume", "merge-audio", "mix-audio",
            "remove-audio-from-video", "remove-noise", "remove-silence", "repair-m4a"
        ],
        "health": "/health"
    }
