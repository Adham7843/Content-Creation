"""Stage 4: Batch Multiplier — 1 source → N meme styles."""

from __future__ import annotations

import logging
from pathlib import Path

from config import MemeConfig, MEME_STYLES

logger = logging.getLogger(__name__)


async def generate_batch(
    config: MemeConfig,
    styles: list[str] | None = None,
) -> list[MemeConfig]:
    """Generate multiple meme configs from one base config.

    Args:
        config: Base configuration.
        styles: List of meme style names to generate. None = all.

    Returns:
        List of configs, one per style variant.
    """
    if styles is None:
        styles = list(MEME_STYLES.keys())

    configs: list[MemeConfig] = []

    for style_name in styles:
        if style_name not in MEME_STYLES:
            continue

        import copy
        variant = copy.deepcopy(config)
        variant.meme_style = style_name
        variant.campaign_name = f"{config.campaign_name or 'meme'}_{style_name}"
        configs.append(variant)

    logger.info("Generated %d style variants", len(configs))
    return configs
