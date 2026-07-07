"""Marketing Video Pipeline — prompt → spec → HTML → render → batch → export.

Usage:
    python pipeline.py "Create a 30 second product launch for Slack"
    python pipeline.py --brief brief.json
    python pipeline.py "Video for Stripe" --batch 12 --template social_ad
"""

from __future__ import annotations

import argparse
import asyncio
import json as json_mod
import logging
import sys
from pathlib import Path
from typing import Optional

from config import (
    VideoBrief,
    RenderConfig,
    BatchVariant,
    get_render_config,
)
from stage1_spec import design_spec
from stage2_html import generate_html
from stage3_render import render_video
from stage4_batch import generate_batch, apply_variant
from stage5_export import export_batch

logger = logging.getLogger("pipeline")

DEFAULT_OUTPUT = Path("output/videos")
DEFAULT_MODEL = "opencode/deepseek-v4-flash-free"


async def run_pipeline(
    user_prompt: Optional[str] = None,
    brief: Optional[VideoBrief] = None,
    template_name: str = "product_launch",
    output_dir: Optional[Path] = None,
    batch_count: int = 1,
    model: str = DEFAULT_MODEL,
) -> list[Path]:
    """Run the complete marketing video pipeline.

    Stages:
        1. Spec Design — user prompt → VideoBrief JSON
        2. HTML Generation — VideoBrief → animated HTML/CSS
        3. Video Render — HTML → MP4/GIF (Playwright + FFmpeg)
        4. Batch Multiply — 1 brief → N variants
        5. Export — organize outputs + metadata

    Args:
        user_prompt: Natural language description of the video.
        brief: Pre-built VideoBrief (skips stage 1).
        template_name: HTML template to use.
        output_dir: Where to save outputs.
        batch_count: Number of variants to generate.
        model: Opencode model for AI stages.

    Returns:
        List of output video paths.
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT
    output_dir.mkdir(parents=True, exist_ok=True)

    # Stage 1: Spec Design
    if brief is None and user_prompt:
        logger.info("=== Stage 1: Spec Design ===")
        brief = await design_spec(user_prompt, opencode_model=model)
        logger.info("Brief: %s — %s", brief.brand_name, brief.headline)
    elif brief is None:
        logger.error("No prompt or brief provided")
        return []

    # Stage 2: HTML Generation
    logger.info("=== Stage 2: HTML Generation ===")
    html = await generate_html(brief, template_name=template_name, opencode_model=model)
    logger.info("HTML generated: %d chars", len(html))

    # Stage 4: Batch (generate variants)
    if batch_count > 1:
        logger.info("=== Stage 4: Batch (%d variants) ===", batch_count)
        variants, variant_paths = await generate_batch(brief, output_dir, batch_count)
    else:
        variants = []
        campaign_dir = output_dir / (brief.brand_name.lower().replace(" ", "_") or "campaign")
        campaign_dir.mkdir(parents=True, exist_ok=True)
        variant_paths = [(
            BatchVariant(variant_id="default", aspect_ratio=brief.aspect_ratio),
            campaign_dir / "video.mp4",
        )]

    # Stage 3: Render each variant
    logger.info("=== Stage 3: Rendering %d videos ===", len(variant_paths))
    video_paths: list[Path] = []

    for variant, vpath in variant_paths:
        variant_brief = apply_variant(brief, variant)
        variant_html = await generate_html(
            variant_brief, template_name=template_name, opencode_model=model,
        )

        render_config = get_render_config(variant_brief)
        result = await render_video(
            variant_html,
            vpath,
            render_config,
            duration_sec=variant_brief.duration_sec,
        )
        if result:
            video_paths.append(result)
            logger.info("Rendered: %s", result)

    # Stage 5: Export
    logger.info("=== Stage 5: Export ===")
    meta_path = await export_batch(video_paths, brief, output_dir)
    logger.info("Metadata: %s", meta_path)

    # Summary
    logger.info("=== Complete: %d videos ===", len(video_paths))
    for vp in video_paths:
        size_mb = vp.stat().st_size / (1024 * 1024) if vp.exists() else 0
        logger.info("  %s (%.1f MB)", vp.name, size_mb)

    return video_paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Marketing Video Harness — generate videos from prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py "Create a 30s product launch video for Slack"
  python pipeline.py "TikTok ad for Stripe" --template social_ad --batch 9
  python pipeline.py --brief my_brief.json --batch 6
        """,
    )
    parser.add_argument(
        "prompt", nargs="?", default=None,
        help="Natural language description of the video",
    )
    parser.add_argument(
        "--brief", "-b", default=None,
        help="Path to a pre-built VideoBrief JSON file (skips stage 1)",
    )
    parser.add_argument(
        "--template", "-t", default="product_launch",
        choices=["product_launch", "testimonial", "explainer", "social_ad", "pricing_promo"],
        help="HTML template to use",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output directory",
    )
    parser.add_argument(
        "--batch", "-n", type=int, default=1,
        help="Number of video variants to generate (default: 1)",
    )
    parser.add_argument(
        "--model", "-m", default=DEFAULT_MODEL,
        help="Opencode model for AI stages",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose logging",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    brief: Optional[VideoBrief] = None

    if args.brief:
        brief_path = Path(args.brief)
        if brief_path.exists():
            data = json_mod.loads(brief_path.read_text())
            brief = VideoBrief(**data)
        else:
            logger.error("Brief file not found: %s", args.brief)
            sys.exit(1)

    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT

    video_paths = asyncio.run(
        run_pipeline(
            user_prompt=args.prompt,
            brief=brief,
            template_name=args.template,
            output_dir=output_dir,
            batch_count=args.batch,
            model=args.model,
        )
    )

    print(f"\n=== Generated {len(video_paths)} video(s) ===")
    print(f"Output: {output_dir}")
    sys.exit(0 if video_paths else 1)


if __name__ == "__main__":
    main()
