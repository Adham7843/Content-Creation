"""Example: Run the marketing video pipeline programmatically."""

import asyncio
import logging
from pathlib import Path

from pipeline import run_pipeline


async def main() -> None:
    video_paths = await run_pipeline(
        user_prompt="Create a 15-second social media ad for a new AI-powered email tool",
        template_name="social_ad",
        output_dir=Path("./example_output"),
        batch_count=3,
    )

    print(f"\nGenerated {len(video_paths)} video(s):")
    for vp in video_paths:
        print(f"  {vp} ({vp.stat().st_size / 1024:.1f} KB)" if vp.exists() else f"  {vp} (missing)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
