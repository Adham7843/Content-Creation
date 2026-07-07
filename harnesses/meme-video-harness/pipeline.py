"""Meme Video Pipeline — source → clip → meme-ify → export.

Usage:
    python pipeline.py "https://youtube.com/watch?v=VIDEO_ID" --style brainrot
    python pipeline.py "https://reddit.com/r/..." --style sigma --clips 7
    python pipeline.py "Some text script" --style tech_bro --source text
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from config import (
    MemeConfig,
    MEME_STYLES,
    TOOLS_ROOT,
    OPENSOURCE_CLIPPING,
    BRAINROTBOT,
)
from stage1_source import fetch_source
from stage2_clip import extract_clips
from stage3_meme import memeify_clips
from stage4_batch import generate_batch
from stage5_export import export_clips

logger = logging.getLogger("meme-pipeline")


async def run_pipeline(
    source_url: str,
    meme_style: str = "brainrot",
    num_clips: int = 5,
    aspect_ratio: str = "9:16",
    source_type: Optional[str] = None,
    output_dir: Optional[Path] = None,
    batch_styles: Optional[list[str]] = None,
) -> list[Path]:
    """Run the full meme video pipeline.

    Stages:
        1. Source — fetch content from URL/text
        2. Clip — AI clip extraction via opensource-clipping
        3. Meme — add meme overlays, captions, effects
        4. Batch — 1 source → N meme styles
        5. Export — organize output

    Tools used:
        - opensource-clipping (F:/Notes/Tools/opensource-clipping/)
        - FFmpeg (system)
        - brainrotbot (F:/Notes/Tools/brainrotbot/) — for Reddit content
    """
    if output_dir is None:
        output_dir = Path("output/clips")

    config = MemeConfig(
        source_url=source_url,
        source_type=source_type or "",
        meme_style=meme_style,
        num_clips=num_clips,
        aspect_ratio=aspect_ratio,
        output_dir=output_dir,
    )

    # Verify tools
    if not OPENSOURCE_CLIPPING.exists():
        logger.error("opensource-clipping not found at %s", OPENSOURCE_CLIPPING)
        logger.error("Clone it: git clone https://github.com/NaufalRizqullah/opensource-clipping.git F:/Notes/Tools/opensource-clipping")
        return []

    if not config.ffmpeg_bin:
        logger.warning("FFmpeg not found — video effects will be skipped")
        logger.warning("Install: winget install ffmpeg")

    logger.info("=== Meme Video Pipeline ===")
    logger.info("Source: %s", source_url[:80])
    logger.info("Style: %s", meme_style)
    logger.info("Clips: %d | Ratio: %s", num_clips, aspect_ratio)

    # Stage 1: Fetch source
    logger.info("--- Stage 1: Fetch Source ---")
    source = await fetch_source(config)
    logger.info("Source type: %s", source["type"])

    # Stage 2: Extract clips
    logger.info("--- Stage 2: Extract Clips (opensource-clipping) ---")
    clips = await extract_clips(config, source)
    logger.info("Clips extracted: %d", len(clips))

    if not clips:
        logger.warning("No clips generated. Is the URL valid and accessible?")
        logger.info("You can run opensource-clipping directly to debug:")
        logger.info("  cd F:/Notes/Tools/opensource-clipping && python main.py --url \"%s\" --clips %d", source_url, num_clips)
        return []

    # Stage 4: Batch (optional — multiple styles)
    all_meme_clips: list[Path] = []
    if batch_styles and len(batch_styles) > 1:
        logger.info("--- Stage 4: Batch (%d styles) ---", len(batch_styles))
        style_configs = await generate_batch(config, batch_styles)
        for sc in style_configs:
            meme_clips = await memeify_clips(clips, sc, source)
            all_meme_clips.extend(meme_clips)
    else:
        # Stage 3: Meme-ify
        logger.info("--- Stage 3: Meme-ify (%s) ---", meme_style)
        all_meme_clips = await memeify_clips(clips, config, source)

    logger.info("Meme clips generated: %d", len(all_meme_clips))

    # Stage 5: Export
    logger.info("--- Stage 5: Export ---")
    meta_path = await export_clips(all_meme_clips, config, source)
    logger.info("Metadata: %s", meta_path)

    # Summary
    logger.info("=== Complete: %d meme clips ===", len(all_meme_clips))
    for mc in all_meme_clips:
        mb = mc.stat().st_size / 1e6 if mc.exists() else 0
        logger.info("  %s (%.1f MB)", mc.name, mb)
    logger.info("Output: %s", output_dir)

    return all_meme_clips


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Meme Video Harness — generate viral meme clips from any content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Styles: {', '.join(MEME_STYLES.keys())}

Examples:
  python pipeline.py "https://youtube.com/watch?v=VIDEO" --style brainrot
  python pipeline.py "https://youtube.com/watch?v=VIDEO" --style sigma --clips 10
  python pipeline.py "https://reddit.com/r/programming/comments/..." --style tech_bro
  python pipeline.py --batch          # Generate ALL 7 styles at once
        """,
    )
    parser.add_argument("url", help="Video URL or text to meme-ify")
    parser.add_argument("--style", "-s", default="brainrot", choices=list(MEME_STYLES.keys()))
    parser.add_argument("--clips", "-n", type=int, default=5)
    parser.add_argument("--ratio", "-r", default="9:16", choices=["9:16", "16:9", "1:1", "3:4", "4:5"])
    parser.add_argument("--source", dest="source_type", choices=["youtube", "reddit", "text", "tiktok", "instagram"])
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--batch", action="store_true", help="Generate ALL 7 meme styles")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    batch_styles = list(MEME_STYLES.keys()) if args.batch else None
    output_dir = Path(args.output) if args.output else Path("output/clips")

    clips = asyncio.run(run_pipeline(
        source_url=args.url,
        meme_style=args.style,
        num_clips=args.clips,
        aspect_ratio=args.ratio,
        source_type=args.source_type,
        output_dir=output_dir,
        batch_styles=batch_styles,
    ))

    print(f"\n=== {len(clips)} meme clips generated ===")
    print(f"Output: {output_dir}")
    sys.exit(0 if clips else 1)


if __name__ == "__main__":
    main()
