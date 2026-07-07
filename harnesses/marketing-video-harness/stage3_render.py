"""Stage 3: Video Renderer — HTML → MP4/GIF via Playwright + FFmpeg.

Captures frames from animated HTML using headless Chromium,
then encodes to video using FFmpeg.

Inspired by HtmlToVideoPixie and RenderGarden.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from config import RenderConfig

logger = logging.getLogger(__name__)


async def render_video(
    html_content: str,
    output_path: Path,
    config: RenderConfig,
    duration_sec: float = 30.0,
) -> Optional[Path]:
    """Render an HTML animation to MP4/GIF video.

    Args:
        html_content: Complete HTML string with CSS animations.
        output_path: Where to save the output video.
        config: Render configuration (resolution, FPS, codec).
        duration_sec: Total animation duration.

    Returns:
        Path to the rendered video, or None if rendering failed.
    """
    logger.info(
        "Rendering video: %dx%d @ %dfps for %.1fs -> %s",
        config.width, config.height, config.fps, duration_sec, output_path,
    )

    # Phase 1: Capture frames via Playwright
    frames_dir = output_path.parent / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    await _capture_frames(html_content, frames_dir, config, duration_sec)

    # Phase 2: Encode to video via FFmpeg
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    if not frame_files:
        logger.error("No frames captured for %s", output_path)
        return None

    await _encode_video(frame_files, output_path, config)

    # Cleanup
    for f in frame_files:
        try:
            f.unlink()
        except OSError:
            pass
    try:
        frames_dir.rmdir()
    except OSError:
        pass

    logger.info("Video rendered: %s", output_path)
    return output_path


async def _capture_frames(
    html_content: str,
    frames_dir: Path,
    config: RenderConfig,
    duration_sec: float,
) -> None:
    """Capture frames using Playwright."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning("Playwright not installed — cannot capture frames")
        return

    total_frames = int(duration_sec * config.fps)
    frame_interval = 1000 / config.fps  # ms

    # Write HTML to temp file
    html_path = frames_dir / "animation.html"
    html_path.write_text(html_content, encoding="utf-8")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": config.width, "height": config.height},
        )

        # Load the HTML file
        file_url = html_path.as_uri()
        await page.goto(file_url, wait_until="networkidle")

        # Wait a moment for first frame to render
        await asyncio.sleep(0.5)

        for frame_num in range(total_frames):
            frame_path = frames_dir / f"frame_{frame_num:06d}.png"
            await page.screenshot(path=str(frame_path))

            # Advance time
            elapsed = (frame_num + 1) * frame_interval / 1000
            if elapsed >= duration_sec:
                break

            await asyncio.sleep(frame_interval / 1000)

        await browser.close()

    # Clean up HTML file
    try:
        html_path.unlink()
    except OSError:
        pass

    logger.info("Captured %d frames to %s", total_frames, frames_dir)


async def _encode_video(
    frame_files: list[Path],
    output_path: Path,
    config: RenderConfig,
) -> None:
    """Encode frames to video using FFmpeg."""
    ffmpeg_bin = _find_ffmpeg()
    if ffmpeg_bin is None:
        logger.error("FFmpeg not found — cannot encode video")
        # Write an empty placeholder
        output_path.write_text("FFmpeg not available")
        return

    frames_pattern = frame_files[0].parent / "frame_%06d.png"

    cmd = [
        ffmpeg_bin,
        "-y",  # overwrite
        "-framerate", str(config.fps),
        "-i", str(frames_pattern),
        "-c:v", config.codec,
        "-preset", config.preset,
        "-crf", str(config.crf),
        "-pix_fmt", config.pix_fmt,
        "-vf", f"scale={config.width}:{config.height}",
    ]

    if config.format == "gif":
        # GIF output
        cmd.extend([
            "-vf", f"fps={config.fps},scale={config.width}:{config.height}:flags=lanczos",
            str(output_path.with_suffix(".gif")),
        ])
        actual_output = output_path.with_suffix(".gif")
    else:
        cmd.extend([
            "-b:v", config.video_bitrate,
            str(output_path),
        ])
        actual_output = output_path

    logger.info("Encoding video: %s", " ".join(cmd))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(), timeout=300
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        logger.error("FFmpeg encoding timed out")
        return

    if proc.returncode != 0:
        stderr_tail = stderr_b.decode("utf-8", errors="replace")[-500:]
        logger.error("FFmpeg failed (exit %d): %s", proc.returncode, stderr_tail)


def _find_ffmpeg() -> Optional[str]:
    """Find FFmpeg binary."""
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if ffmpeg:
        return ffmpeg

    # Common Windows paths
    common = [
        Path("C:/ffmpeg/bin/ffmpeg.exe"),
        Path.home() / "ffmpeg/bin/ffmpeg.exe",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "ffmpeg/bin/ffmpeg.exe",
    ]
    for p in common:
        if p.exists():
            return str(p)

    return None
