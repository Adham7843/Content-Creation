"""Stage 5: Export — organize outputs, generate metadata, thumbnails.

Clean up batch output into organized folders with metadata.
"""

from __future__ import annotations

import json as json_mod
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import VideoBrief

logger = logging.getLogger(__name__)


async def export_batch(
    video_paths: list[Path],
    brief: VideoBrief,
    output_dir: Path,
    campaign_name: Optional[str] = None,
) -> Path:
    """Organize and export a batch of videos.

    Args:
        video_paths: List of rendered video file paths.
        brief: The original video brief.
        output_dir: Where to organize outputs.
        campaign_name: Name for this campaign batch.

    Returns:
        Path to the metadata.json file.
    """
    if campaign_name is None:
        campaign_name = (
            brief.campaign_name
            or brief.brand_name.lower().replace(" ", "_")
            or "campaign"
        )

    campaign_dir = output_dir / campaign_name
    campaign_dir.mkdir(parents=True, exist_ok=True)

    # Move/copy videos to campaign dir
    final_paths: list[Path] = []
    for vp in video_paths:
        if vp.exists():
            dest = campaign_dir / vp.name
            import shutil
            shutil.copy2(str(vp), str(dest))
            final_paths.append(dest)

    # Write metadata
    metadata = {
        "campaign": campaign_name,
        "brand": brief.brand_name,
        "product": brief.product_name,
        "headline": brief.headline,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "video_count": len(final_paths),
        "videos": [
            {
                "filename": p.name,
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
            for p in final_paths
        ],
        "spec": {
            "tone": brief.tone,
            "style": brief.style,
            "aspect_ratios": list(set(
                brief.aspect_ratio
            )),
            "cta": brief.cta_text,
        },
    }

    meta_path = campaign_dir / "metadata.json"
    meta_path.write_text(
        json_mod.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logger.info(
        "Exported %d videos to %s", len(final_paths), campaign_dir
    )
    return meta_path
