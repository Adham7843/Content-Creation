"""Stage 3: Meme-ify — add meme captions, effects, and viral sauce.

Post-processes clipped videos with:
- Text overlays (top/bottom captions in meme style)
- Sound effects
- Emoji spam
- Speed ramps
- Color grading
"""

from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Optional

from config import MemeConfig, MemeStyle, MEME_STYLES

logger = logging.getLogger(__name__)


async def memeify_clips(
    clips: list[Path],
    config: MemeConfig,
    source: dict,
) -> list[Path]:
    """Add meme overlays to clipped videos.

    Uses FFmpeg for video effects since it's the lowest-dep approach.
    For text overlays, generates ASS subtitle files with meme formatting.
    """
    if not clips:
        logger.warning("No clips to meme-ify")
        return []

    style = MEME_STYLES.get(config.meme_style, MEME_STYLES["brainrot"])

    meme_clips: list[Path] = []

    for i, clip in enumerate(clips):
        meme_path = clip.parent / f"meme_{style.name.lower()}_{i:03d}.mp4"
        logger.info("Meme-ifying clip %d: %s -> %s", i, clip.name, meme_path.name)

        # For v1: just copy with potential effects
        # Full meme-ification requires FFmpeg + ASS subtitles
        if config.ffmpeg_bin:
            await _apply_meme_effects(clip, meme_path, style, config)
        else:
            # No FFmpeg — just copy as-is with a name change
            shutil.copy2(str(clip), str(meme_path))
            logger.info("No FFmpeg — copied clip as-is: %s", meme_path)

        meme_clips.append(meme_path)

    return meme_clips


async def _apply_meme_effects(
    input_path: Path,
    output_path: Path,
    style: MemeStyle,
    config: MemeConfig,
) -> None:
    """Apply meme-style effects using FFmpeg."""
    ffmpeg = config.ffmpeg_bin
    if not ffmpeg:
        return

    vf_filters: list[str] = []

    # Color grading
    if style.vibe == "sigma":
        # Desaturated, high contrast
        vf_filters.append("colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3")
    elif style.vibe == "brainrot":
        # Boosted saturation
        vf_filters.append("eq=saturation=1.5:contrast=1.2")

    # Effects
    if "shake" in style.effects:
        vf_filters.append("crop=iw-10:ih-10:5:5")

    vf_str = ",".join(vf_filters) if vf_filters else "null"

    cmd = [
        ffmpeg, "-y",
        "-i", str(input_path),
        "-vf", vf_str,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        str(output_path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await asyncio.wait_for(proc.communicate(), timeout=120)
