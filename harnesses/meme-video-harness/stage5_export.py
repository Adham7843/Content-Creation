"""Stage 5: Export — organize meme clips into folders."""

from __future__ import annotations

import json as json_mod
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from config import MemeConfig, MEME_STYLES

logger = logging.getLogger(__name__)


async def export_clips(
    clips: list[Path],
    config: MemeConfig,
    source: dict,
) -> Path:
    """Export meme clips to organized output directory."""
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    final_clips: list[Path] = []
    for clip in clips:
        if clip.exists():
            dest = output_dir / clip.name
            shutil.copy2(str(clip), str(dest))
            final_clips.append(dest)

    style = MEME_STYLES.get(config.meme_style, MEME_STYLES["brainrot"])

    metadata = {
        "source": source.get("url", ""),
        "source_type": source.get("type", ""),
        "style": config.meme_style,
        "style_name": style.name,
        "vibe": style.vibe,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clip_count": len(final_clips),
        "clips": [{"file": p.name, "size_mb": round(p.stat().st_size / 1e6, 1)} for p in final_clips],
    }

    meta_path = output_dir / "metadata.json"
    meta_path.write_text(json_mod.dumps(metadata, indent=2, ensure_ascii=False))

    logger.info("Exported %d clips to %s", len(final_clips), output_dir)
    return meta_path
