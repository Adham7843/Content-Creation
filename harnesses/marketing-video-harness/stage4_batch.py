"""Stage 4: Batch Multiplier — 1 VideoBrief → N video variants.

Generates multiple variants of a video by varying:
- Aspect ratios (16:9, 9:16, 1:1, 4:5)
- CTA text variations
- Color schemes
- Duration (15s, 30s, 60s)
- Headline variations
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from config import VideoBrief, BatchVariant, get_render_config, ASPECT_RATIOS

logger = logging.getLogger(__name__)

# Predefined CTA variations
CTA_VARIATIONS = [
    "Learn More",
    "Get Started Free",
    "Try It Now",
    "See Plans",
    "Start Your Trial",
    "Book a Demo",
    "Join Now",
    "Claim Your Offer",
]

# Color scheme variations
COLOR_SCHEMES = [
    ("#6C63FF", "#FF6584"),  # Purple + Pink
    ("#00B4DB", "#0083B0"),  # Blue gradient
    ("#FF512F", "#F09819"),  # Orange + Yellow
    ("#11998E", "#38EF7D"),  # Green gradient
    ("#FC466B", "#3F5EFB"),  # Pink + Blue
    ("#1A1A2E", "#E94560"),  # Dark + Red
]


async def generate_batch(
    brief: VideoBrief,
    output_dir: Path,
    variant_count: int = 6,
) -> list[tuple[BatchVariant, Path]]:
    """Generate multiple video variants from one brief.

    Args:
        brief: The base video brief.
        output_dir: Directory to store variants.
        variant_count: How many variants to generate.

    Returns:
        List of (variant, output_path) tuples.
    """
    logger.info("Generating %d variants for %s", variant_count, brief.brand_name)

    variants = _build_variants(brief, variant_count)
    results: list[tuple[BatchVariant, Path]] = []

    for i, variant in enumerate(variants):
        variant_dir = output_dir / f"variant_{i:03d}"
        variant_dir.mkdir(parents=True, exist_ok=True)
        output_path = variant_dir / f"{variant.variant_id}.mp4"
        results.append((variant, output_path))

    return results


def _build_variants(brief: VideoBrief, count: int) -> list[BatchVariant]:
    """Build variant configurations."""
    variants: list[BatchVariant] = []
    ratios = list(ASPECT_RATIOS.keys())

    for i in range(count):
        color_idx = i % len(COLOR_SCHEMES)
        cta_idx = i % len(CTA_VARIATIONS)
        ratio_idx = i % len(ratios)

        primary, secondary = COLOR_SCHEMES[color_idx]
        cta = CTA_VARIATIONS[cta_idx]
        ratio = ratios[ratio_idx]

        duration = 30.0
        if i % 3 == 1:
            duration = 15.0
        elif i % 3 == 2:
            duration = 60.0

        variants.append(BatchVariant(
            variant_id=f"{ratio.replace(':', 'x')}_{int(duration)}s",
            aspect_ratio=ratio,
            duration_sec=duration,
            cta_text=cta,
            primary_color=primary,
        ))

    return variants


def apply_variant(brief: VideoBrief, variant: BatchVariant) -> VideoBrief:
    """Create a modified brief by applying a variant."""
    import copy
    import dataclasses

    new_brief = copy.deepcopy(brief)
    new_brief.aspect_ratio = variant.aspect_ratio
    new_brief.duration_sec = variant.duration_sec

    if variant.cta_text:
        new_brief.cta_text = variant.cta_text
    if variant.primary_color:
        new_brief.primary_color = variant.primary_color
    if variant.headline:
        new_brief.headline = variant.headline

    # Adjust scenes for duration
    scene_count = len(new_brief.scenes) or 3
    scene_dur = variant.duration_sec / (scene_count + 1)  # +1 for CTA scene

    for scene in new_brief.scenes:
        scene.duration_sec = round(scene_dur, 1)

    # Update output name
    safe_name = new_brief.brand_name.lower().replace(" ", "_") if new_brief.brand_name else "video"
    new_brief.output_name = f"{safe_name}_{variant.variant_id}"

    return new_brief
