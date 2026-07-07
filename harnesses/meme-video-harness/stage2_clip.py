"""Stage 2: AI Clip Extractor — runs opensource-clipping to extract viral moments.

Calls: python F:/Notes/Tools/opensource-clipping/main.py --url <url> --clips N
"""

from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Optional

from config import MemeConfig, MemeStyle, MEME_STYLES

logger = logging.getLogger(__name__)


async def extract_clips(
    config: MemeConfig,
    source: dict,
) -> list[Path]:
    """Run opensource-clipping to extract viral clip moments.

    Args:
        config: Meme configuration.
        source: Source info from stage 1.

    Returns:
        List of paths to generated clip files.
    """
    url = source.get("url", config.source_url)
    if not url:
        logger.error("No source URL to clip")
        return []

    style = MEME_STYLES.get(config.meme_style, MEME_STYLES["brainrot"])
    num_clips = config.num_clips
    ratio = config.aspect_ratio

    main_py = config.clipping_tool / "main.py"
    if not main_py.exists():
        logger.error("opensource-clipping not found at %s", main_py)
        return []

    python_bin = shutil.which("python") or shutil.which("python3") or "python"

    cmd = [
        python_bin,
        str(main_py),
        "--url", url,
        "--clips", str(num_clips),
        "--ratio", ratio,
        "--font-style", style.font_style,
    ]

    if not config.with_hook:
        cmd.append("--no-hook")
    if config.with_hook:
        cmd.append("--hook-v2")
    if not config.with_subs:
        cmd.append("--no-subs")
    if not config.with_bgm:
        cmd.append("--no-bgm")
    if config.with_broll:
        cmd.extend(["--no-broll"])  # Inverted: we pass --no-broll to DISABLE
    else:
        cmd.append("--no-broll")
    if not config.with_bgm:
        cmd.append("--no-bgm")
    if config.face_detector == "yolo":
        cmd.extend(["--face-detector", "yolo"])

    # Source type override
    stype = source.get("type", "youtube")
    if stype != "youtube":
        cmd.extend(["--source", stype])

    logger.info("Running opensource-clipping: %s", " ".join(cmd[:8]))

    # Run in the clipping tool directory
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(config.clipping_tool),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(), timeout=1800  # 30 min for AI processing
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        logger.error("opensource-clipping timed out")
        return []

    if proc.returncode != 0:
        stderr_tail = stderr_b.decode("utf-8", errors="replace")[-1000:]
        logger.warning("Clipping exited %d: %s", proc.returncode, stderr_tail)

    # Find output clips
    outputs_dir = config.clipping_tool / "outputs"
    clips: list[Path] = []
    if outputs_dir.exists():
        clips = sorted(outputs_dir.glob("*_ready.mp4"))
        logger.info("Found %d clips in %s", len(clips), outputs_dir)

    return clips
