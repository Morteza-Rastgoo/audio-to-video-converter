import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import subprocess
import tempfile
import requests
from pydantic import BaseModel
from typing import List, Optional, Dict

app = FastAPI(title="Video Audio Tools API", description="Comprehensive audio and video processing tools")

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

# Probe models
class ProbeRequest(BaseModel):
    media_url: str

class ThumbnailRequest(BaseModel):
    video_url: str
    timestamp: str = "00:00:01"  # HH:MM:SS format
    width: int = 320
    height: int = 240

class WaveformRequest(BaseModel):
    audio_url: str
    width: int = 800
    height: int = 200
    color: str = "blue"

# Video Effects models
class VideoEffectOption(BaseModel):
    option: str
    argument: str

class VideoEffectInput(BaseModel):
    file_url: str
    options: List[VideoEffectOption] = []

class VideoEffectFilter(BaseModel):
    filter: str

class VideoEffectOutput(BaseModel):
    options: List[VideoEffectOption] = []

class VideoEffectMetadata(BaseModel):
    duration: bool = False
    filesize: bool = False

class VideoEffectRequest(BaseModel):
    id: str
    inputs: List[VideoEffectInput]
    filters: List[VideoEffectFilter] = []
    outputs: List[VideoEffectOutput] = []
    metadata: VideoEffectMetadata = VideoEffectMetadata()

# Simplified effect request model
class SimpleEffectRequest(BaseModel):
    url: str
    effect: str
    duration: float = 39.5  # Default pan duration
    width: int = 1080
    height: int = 1920
    output_format: str = "mp4"

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
            filter_complex = "scale=w=1920:h=1080:force_original_aspect_ratio=increase,crop=1920:1080:x='(iw-1920)*(t/5)':y=0"
        elif request.effect == "pan_right":
            filter_complex = "scale=w=1920:h=1080:force_original_aspect_ratio=increase,crop=1920:1080:x='(iw-1920)*(1-t/5)':y=0"
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
        cmd.extend(["-c:a", "libmp3lame", "-y", output_path])
        
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
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c:a", "libmp3lame", "-y", output_path]
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

# Probe endpoints
@app.post("/probe-media")
async def probe_media(request: ProbeRequest):
    """Get comprehensive information about audio/video files using ffprobe"""
    temp_dir = tempfile.mkdtemp()
    try:
        media_path = download_file(request.media_url, temp_dir, "media")
        
        # Get basic format information
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", 
            "-show_streams", "-show_chapters", media_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to probe media file")
        
        probe_data = json.loads(result.stdout)
        
        # Extract useful information
        info = {
            "filename": probe_data.get("format", {}).get("filename", ""),
            "format": probe_data.get("format", {}).get("format_name", ""),
            "duration": float(probe_data.get("format", {}).get("duration", 0)),
            "size": int(probe_data.get("format", {}).get("size", 0)),
            "bitrate": int(probe_data.get("format", {}).get("bit_rate", 0)),
            "streams": []
        }
        
        # Process streams
        for stream in probe_data.get("streams", []):
            stream_info = {
                "index": stream.get("index", 0),
                "type": stream.get("codec_type", ""),
                "codec": stream.get("codec_name", ""),
                "language": stream.get("tags", {}).get("language", "und")
            }
            
            if stream.get("codec_type") == "video":
                stream_info.update({
                    "width": stream.get("width", 0),
                    "height": stream.get("height", 0),
                    "fps": eval(stream.get("r_frame_rate", "0/1")),
                    "pixel_format": stream.get("pix_fmt", ""),
                    "duration": float(stream.get("duration", 0))
                })
            elif stream.get("codec_type") == "audio":
                stream_info.update({
                    "channels": stream.get("channels", 0),
                    "sample_rate": int(stream.get("sample_rate", 0)),
                    "bitrate": int(stream.get("bit_rate", 0)),
                    "duration": float(stream.get("duration", 0))
                })
            
            info["streams"].append(stream_info)
        
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-duration")
async def get_duration(request: ProbeRequest):
    """Get duration of audio/video file"""
    temp_dir = tempfile.mkdtemp()
    try:
        media_path = download_file(request.media_url, temp_dir, "media")
        
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", media_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to get duration")
        
        duration = float(result.stdout.strip())
        
        # Convert to human readable format
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration % 1) * 1000)
        
        return {
            "duration_seconds": duration,
            "duration_formatted": f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}",
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "milliseconds": milliseconds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-thumbnail")
async def get_thumbnail(request: ThumbnailRequest):
    """Extract thumbnail/frame from video at specific timestamp"""
    temp_dir = tempfile.mkdtemp()
    try:
        video_path = download_file(request.video_url, temp_dir, "video")
        output_path = os.path.join(temp_dir, "thumbnail.jpg")
        
        cmd = [
            "ffmpeg", "-i", video_path, "-ss", request.timestamp, 
            "-vframes", "1", "-q:v", "2", "-vf", 
            f"scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2",
            "-y", output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return FileResponse(output_path, media_type='image/jpeg', filename="thumbnail.jpg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-waveform")
async def get_waveform(request: WaveformRequest):
    """Generate waveform visualization for audio file"""
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "audio")
        output_path = os.path.join(temp_dir, "waveform.png")
        
        cmd = [
            "ffmpeg", "-i", audio_path, "-filter_complex", 
            f"showwavespic=s={request.width}x{request.height}:colors={request.color}",
            "-frames:v", "1", "-y", output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return FileResponse(output_path, media_type='image/png', filename="waveform.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-audio-info")
async def get_audio_info(request: ProbeRequest):
    """Get detailed audio file information"""
    temp_dir = tempfile.mkdtemp()
    try:
        audio_path = download_file(request.audio_url, temp_dir, "audio")
        
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", 
            "-show_streams", "-select_streams", "a:0", audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to probe audio file")
        
        probe_data = json.loads(result.stdout)
        
        format_info = probe_data.get("format", {})
        stream_info = probe_data.get("streams", [{}])[0] if probe_data.get("streams") else {}
        
        return {
            "filename": format_info.get("filename", ""),
            "format": format_info.get("format_name", ""),
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bitrate": int(format_info.get("bit_rate", 0)),
            "codec": stream_info.get("codec_name", ""),
            "channels": stream_info.get("channels", 0),
            "sample_rate": int(stream_info.get("sample_rate", 0)),
            "bits_per_sample": int(stream_info.get("bits_per_sample", 0)),
            "tags": stream_info.get("tags", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-video-info")
async def get_video_info(request: ProbeRequest):
    """Get detailed video file information"""
    temp_dir = tempfile.mkdtemp()
    try:
        video_path = download_file(request.video_url, temp_dir, "video")
        
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", 
            "-show_streams", "-select_streams", "v:0", video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to probe video file")
        
        probe_data = json.loads(result.stdout)
        
        format_info = probe_data.get("format", {})
        stream_info = probe_data.get("streams", [{}])[0] if probe_data.get("streams") else {}
        
        # Calculate frame rate
        fps = 0
        if stream_info.get("r_frame_rate"):
            try:
                num, den = stream_info["r_frame_rate"].split("/")
                fps = float(num) / float(den)
            except:
                fps = 0
        
        return {
            "filename": format_info.get("filename", ""),
            "format": format_info.get("format_name", ""),
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bitrate": int(format_info.get("bit_rate", 0)),
            "codec": stream_info.get("codec_name", ""),
            "width": stream_info.get("width", 0),
            "height": stream_info.get("height", 0),
            "fps": round(fps, 2),
            "pixel_format": stream_info.get("pix_fmt", ""),
            "aspect_ratio": stream_info.get("display_aspect_ratio", ""),
            "tags": stream_info.get("tags", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Video Effects endpoint
@app.post("/apply-video-effect")
async def apply_video_effect(request: VideoEffectRequest):
    """Apply video effects using FFmpeg filter chains"""
    temp_dir = tempfile.mkdtemp()
    try:
        # Download input files
        input_paths = []
        for i, input_item in enumerate(request.inputs):
            filename = f"input_{i}.mp4"
            path = download_file(input_item.file_url, temp_dir, filename)
            input_paths.append(path)
        
        output_path = os.path.join(temp_dir, "output.mp4")
        
        # Build FFmpeg command
        cmd = ["ffmpeg"]
        
        # Add input options and files
        for input_item in request.inputs:
            for option in input_item.options:
                cmd.extend([option.option, option.argument])
            # Add the input file
            cmd.extend(["-i", input_paths[request.inputs.index(input_item)]])
        
        # Add filter complex if filters are provided
        if request.filters:
            filter_parts = []
            for filter_item in request.filters:
                filter_parts.append(filter_item.filter)
            filter_complex = ",".join(filter_parts)
            cmd.extend(["-filter_complex", filter_complex])
        
        # Add output options
        for output_item in request.outputs:
            for option in output_item.options:
                cmd.extend([option.option, option.argument])
        
        # Default output settings if no output options provided
        if not request.outputs:
            cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-y", output_path])
        else:
            cmd.extend(["-y", output_path])
        
        # Execute FFmpeg command
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Get metadata if requested
        response_data = {"output_url": "processed_video.mp4"}
        
        if request.metadata.duration or request.metadata.filesize:
            metadata = {}
            if request.metadata.duration:
                duration_cmd = [
                    "ffprobe", "-v", "error", "-show_entries", "format=duration", 
                    "-of", "default=noprint_wrappers=1:nokey=1", output_path
                ]
                duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
                if duration_result.returncode == 0:
                    metadata["duration"] = float(duration_result.stdout.strip())
            
            if request.metadata.filesize:
                metadata["filesize"] = os.path.getsize(output_path)
            
            response_data["metadata"] = metadata
        
        # Return the processed video file
        return FileResponse(output_path, media_type='video/mp4', filename="processed_video.mp4")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/apply-effect")
async def apply_simple_effect(request: SimpleEffectRequest):
    """Apply predefined video effects with simple parameters"""
    temp_dir = tempfile.mkdtemp()
    try:
        # Download the input file
        input_path = download_file(request.url, temp_dir, "input")
        
        output_path = os.path.join(temp_dir, f"output.{request.output_format}")
        
        # Check if input is an image (needs looping for effects)
        is_image = not any(ext in request.url.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.mp3', '.wav', '.aac'])
        
        # Get input dimensions for proper aspect ratio handling
        input_width, input_height = request.width, request.height
        if is_image:
            try:
                # Use ffprobe to get actual image dimensions
                probe_cmd = [
                    "ffprobe", "-v", "error", "-select_streams", "v:0", 
                    "-show_entries", "stream=width,height", "-of", "csv=p=0", input_path
                ]
                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                if probe_result.returncode == 0:
                    dims = probe_result.stdout.strip().split(',')
                    if len(dims) == 2:
                        input_width = int(dims[0])
                        input_height = int(dims[1])
            except:
                # Fallback to request dimensions if probing fails
                pass
        
        # Define effect configurations
        effect_configs = {
            "pan_crop_vertical": {
                "requires_loop": True,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"scale=w=1080:h=1920:force_original_aspect_ratio=increase,crop=1080:1920:x='(iw-1080)*(1-t/5)':y=0,fps=30"],
                "output_options": [
                    {"option": "-t", "argument": str(request.duration)},
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "zoom_in_center": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(max(zoom,pzoom)+0.0015,2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={request.width}x{request.height}"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "fade_in_out": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"fade=t=in:st=0:d=1,fade=t=out:st={max(1, request.duration-1)}:d=1,scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "blur": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"boxblur=10,scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "sepia": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "grayscale": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"format=gray,scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "vignette": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"vignette=PI/4,scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "mirror_flip": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"hflip,scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "speed_up": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"{'setpts=PTS/2,' if not is_image else ''}scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            },
            "slow_down": {
                "requires_loop": False,
                "input_options": [{"option": "-loop", "argument": "1"}] if is_image else [],
                "filters": [f"{'setpts=PTS*2,' if not is_image else ''}scale={request.width}:{request.height}:force_original_aspect_ratio=decrease,pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2"],
                "output_options": [
                    {"option": "-c:v", "argument": "libx264"},
                    {"option": "-pix_fmt", "argument": "yuv420p"}
                ]
            }
        }
        
        if request.effect not in effect_configs:
            raise HTTPException(status_code=400, detail=f"Effect '{request.effect}' not supported. Available effects: {', '.join(effect_configs.keys())}")
        
        # Special handling for pan_crop_vertical - use the working approach
        if request.effect == "pan_crop_vertical":
            # Use the exact same logic as the working /apply-video-effect curl command
            temp_dir = tempfile.mkdtemp()
            try:
                # Download input file
                input_path = download_file(request.url, temp_dir, "input")
                
                output_path = os.path.join(temp_dir, f"output.{request.output_format}")
                
                # Build FFmpeg command exactly like the working curl
                cmd = ["ffmpeg"]
                
                # Add input options
                cmd.extend(["-loop", "1"])
                cmd.extend(["-i", input_path])
                
                # Add filter complex - exact same as working
                filter_str = "scale=w=1080:h=1920:force_original_aspect_ratio=increase,crop=1080:1920:x='(iw-1080)*(1-t/5)':y=0,fps=30"
                cmd.extend(["-filter_complex", filter_str])
                
                # Add output options
                cmd.extend(["-t", str(request.duration)])
                cmd.extend(["-c:v", "libx264"])
                cmd.extend(["-pix_fmt", "yuv420p"])
                cmd.extend(["-y", output_path])
                
                # Execute FFmpeg command with capture_output=True like /apply-video-effect
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Return the processed video file
                return FileResponse(output_path, media_type=f'video/{request.output_format}', filename=f"effect_{request.effect}.{request.output_format}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        config = effect_configs[request.effect]
        
        # Build output options based on input type
        output_options = []
        if is_image:
            output_options.append({"option": "-t", "argument": str(request.duration)})
        output_options.extend([
            {"option": "-c:v", "argument": "libx264"},
            {"option": "-pix_fmt", "argument": "yuv420p"}
        ])
        
        # Build FFmpeg command
        cmd = ["ffmpeg"]
        
        # Add input options and file
        for option in config["input_options"]:
            cmd.extend([option["option"], option["argument"]])
        cmd.extend(["-i", input_path])
        
        # Add filters
        if config["filters"]:
            filter_complex = ",".join(config["filters"])
            cmd.extend(["-filter_complex", filter_complex])
        
        # Add output options
        for option in output_options:
            cmd.extend([option["option"], option["argument"]])
        
        # Add output file
        cmd.extend(["-y", output_path])
        
        # Execute FFmpeg command
        subprocess.run(cmd, check=True)
        
        # Return the processed video file
        return FileResponse(output_path, media_type=f'video/{request.output_format}', filename=f"effect_{request.effect}.{request.output_format}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video-effects")
async def get_video_effects():
    """Get list of predefined video effects with examples"""
    return {
        "effects": {
            "pan_crop_vertical": {
                "description": "Pan and crop image to vertical video format",
                "example": {
                    "id": "pan_crop_vertical",
                    "inputs": [
                        {
                            "file_url": "https://example.com/image.jpg",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(ow-iw)/2:(oh-ih)/2"
                        }
                    ],
                    "outputs": [
                        {
                            "options": [
                                {"option": "-c:v", "argument": "libx264"},
                                {"option": "-tune", "argument": "stillimage"},
                                {"option": "-preset", "argument": "fast"}
                            ]
                        }
                    ],
                    "metadata": {"duration": True}
                }
            },
            "zoom_in_center": {
                "description": "Zoom in to center of video",
                "example": {
                    "id": "zoom_in_center",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "zoompan=z='min(max(zoom,pzoom)+0.0015,2)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "fade_in_out": {
                "description": "Add fade in and fade out effects",
                "example": {
                    "id": "fade_in_out",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "fade=t=in:st=0:d=1,fade=t=out:st=4:d=1"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "blur_background": {
                "description": "Apply blur effect to video background",
                "example": {
                    "id": "blur_background",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "boxblur=10"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "sepia_tone": {
                "description": "Apply sepia color effect",
                "example": {
                    "id": "sepia_tone",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "speed_ramp": {
                "description": "Apply speed ramping effect (slow to fast)",
                "example": {
                    "id": "speed_ramp",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "setpts=PTS*2-2*PTS*exp(-PTS),atempo=1+exp(-PTS)"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "vignette": {
                "description": "Add vignette effect to video",
                "example": {
                    "id": "vignette",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "vignette=PI/4"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "mirror_flip": {
                "description": "Mirror flip the video horizontally",
                "example": {
                    "id": "mirror_flip",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "hflip"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "grayscale": {
                "description": "Convert video to grayscale",
                "example": {
                    "id": "grayscale",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "format=gray"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "stabilize": {
                "description": "Apply video stabilization",
                "example": {
                    "id": "stabilize",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "vidstabdetect=shakiness=10:accuracy=15,vidstabtransform=smoothing=30"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            },
            "text_overlay": {
                "description": "Add text overlay to video",
                "example": {
                    "id": "text_overlay",
                    "inputs": [
                        {
                            "file_url": "https://example.com/video.mp4",
                            "options": []
                        }
                    ],
                    "filters": [
                        {
                            "filter": "drawtext=text='Sample Text':fontsize=50:fontcolor=white:x=100:y=100"
                        }
                    ],
                    "outputs": [],
                    "metadata": {"duration": True}
                }
            }
        },
        "usage": "Use /apply-video-effect endpoint with the example JSON structures above"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "video-audio-tools"}

@app.get("/")
async def root():
    return {
        "message": "Video Audio Tools API",
        "version": "3.3",
        "tools": [
            "audio-to-video", "change-speed", "compress-mp3", "cut-mp3",
            "extract-audio", "change-volume", "merge-audio", "mix-audio",
            "remove-audio-from-video", "remove-noise", "remove-silence", "repair-m4a"
        ],
        "probe_tools": [
            "probe-media", "get-duration", "get-thumbnail", "get-waveform",
            "get-audio-info", "get-video-info"
        ],
        "video_effects": [
            "apply-effect", "apply-video-effect", "video-effects"
        ],
        "health": "/health"
    }
