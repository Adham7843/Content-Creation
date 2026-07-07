"""Simple Clip + Caption — split video, add meme captions, done.
No AI. No APIs. Just FFmpeg.

Usage:
    python clipper.py video.mp4 --caption "When the code finally works" --clips 5
    python clipper.py video.mp4 --captions captions.txt --clip-length 15
"""

import argparse
import subprocess
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Split video into meme clips with captions")
    parser.add_argument("video", help="Video file or YouTube URL")
    parser.add_argument("--caption", "-c", help="Single caption for all clips")
    parser.add_argument("--captions", "-f", help="Text file with one caption per line")
    parser.add_argument("--clips", "-n", type=int, default=5, help="Number of clips")
    parser.add_argument("--clip-length", "-l", type=int, default=10, help="Clip length in seconds")
    parser.add_argument("--output", "-o", default="output/clips", help="Output directory")
    parser.add_argument("--style", "-s", default="brainrot", 
                       choices=["brainrot","minimal","bold","clean"])
    parser.add_argument("--ratio", "-r", default="9:16", choices=["9:16","16:9","1:1"])
    
    args = parser.parse_args()
    
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        print("[!] FFmpeg not found. Install: winget install ffmpeg")
        return
    
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    
    # Resolve video
    video_path = _resolve(args.video)
    if not video_path:
        return
    
    # Determine duration
    duration = _get_duration(video_path, ffmpeg)
    if duration == 0:
        print("[!] Could not determine video duration")
        return
    
    # Get captions
    captions = _get_captions(args)
    
    # Calculate clip starts (spread across video)
    clip_len = args.clip_length
    usable = max(0, duration - clip_len)
    step = usable / max(args.clips, 1)
    
    style = _styles(args.style)
    
    print(f"Video: {duration:.0f}s | Clips: {args.clips} x {clip_len}s | Style: {args.style}")
    print(f"Ratio: {args.ratio}")
    
    for i in range(args.clips):
        start = min(i * step, usable)
        cap = captions[i % len(captions)] if captions else f"Clip {i+1}"
        
        clip_path = out / f"clip_{i:03d}_{args.style}.mp4"
        
        _make_clip(ffmpeg, video_path, clip_path, start, clip_len, cap, style, args.ratio)
        print(f"  [{i+1}/{args.clips}] {cap[:40]} -> {clip_path.name}")


def _resolve(path: str) -> str | None:
    """Resolve file or YouTube URL."""
    p = Path(path)
    if p.exists():
        return str(p)
    
    # Try yt-dlp for YouTube
    ytdlp = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if ytdlp and ("youtube.com" in path or "youtu.be" in path):
        print("Downloading from YouTube...")
        out = Path("output") / "source.mp4"
        out.parent.mkdir(exist_ok=True)
        subprocess.run([ytdlp, "-f", "mp4", "-o", str(out), path], check=False)
        if out.exists():
            return str(out)
    
    print(f"[!] Video not found: {path}")
    return None


def _get_duration(video: str, ffmpeg: str) -> float:
    """Get video duration in seconds."""
    try:
        r = subprocess.run(
            [ffmpeg, "-i", video], 
            capture_output=True, text=True, timeout=30
        )
        import re
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
        if m:
            return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
    except Exception:
        pass
    return 0


def _get_captions(args) -> list[str]:
    """Get caption list."""
    if args.captions:
        p = Path(args.captions)
        if p.exists():
            return [l.strip() for l in p.read_text().splitlines() if l.strip()]
    if args.caption:
        return [args.caption]
    return []


def _styles(style: str) -> dict:
    """Style presets."""
    return {
        "brainrot": {"fontsize": 56, "fontcolor": "yellow", "bordercolor": "black", "borderw": 3, "pos": "bottom"},
        "minimal":  {"fontsize": 40, "fontcolor": "white",  "bordercolor": "black", "borderw": 2, "pos": "bottom"},
        "bold":     {"fontsize": 64, "fontcolor": "white",  "bordercolor": "red",   "borderw": 4, "pos": "center"},
        "clean":    {"fontsize": 36, "fontcolor": "white",  "bordercolor": "black", "borderw": 1, "pos": "bottom"},
    }.get(style, {})


def _make_clip(ffmpeg: str, video: str, out: Path, start: float, length: float, 
               caption: str, style: dict, ratio: str):
    """Create one clip with caption overlay."""
    fs = style.get("fontsize", 48)
    fc = style.get("fontcolor", "white")
    bc = style.get("bordercolor", "black")
    bw = style.get("borderw", 2)
    pos = style.get("pos", "bottom")
    
    # Escape caption for FFmpeg
    cap = caption.replace("'", "'\\''").replace(":", "\\:").replace("%", "\\%")
    
    # Position
    if pos == "bottom":
        y_pos = "h-th-30"
    elif pos == "center":
        y_pos = "(h-th)/2"
    else:
        y_pos = "h-th-30"
    
    # Drawtext filter
    drawtext = (
        f"drawtext=text='{cap}':"
        f"fontsize={fs}:fontcolor={fc}:bordercolor={bc}:borderw={bw}:"
        f"x=(w-text_w)/2:y={y_pos}:"
        f"fontfile=/Windows/Fonts/impact.ttf"
    )
    
    # Crop for aspect ratio
    crop = ""
    if ratio == "9:16":
        crop = "crop=ih*9/16:ih,"
    elif ratio == "1:1":
        crop = "crop=min(iw\\,ih):min(iw\\,ih),"
    
    cmd = [
        ffmpeg, "-y",
        "-ss", str(start),
        "-t", str(length),
        "-i", video,
        "-vf", f"{crop}{drawtext}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out),
    ]
    
    subprocess.run(cmd, capture_output=True, timeout=120)


if __name__ == "__main__":
    main()
