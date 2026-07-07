"""Stage 1: Spec Designer — chat with agent to produce structured VideoBrief.

Uses Opencode as a subprocess with a spec-designer prompt.
The agent asks clarifying questions, then outputs a structured JSON spec.
"""

from __future__ import annotations

import asyncio
import json as json_mod
import logging
import tempfile
from pathlib import Path
from typing import Optional

from config import VideoBrief, Scene

logger = logging.getLogger(__name__)


async def design_spec(
    user_prompt: str,
    opencode_model: str = "opencode/deepseek-v4-flash-free",
    timeout_sec: int = 300,
) -> VideoBrief:
    """Run a spec-designing agent conversation to produce a VideoBrief.

    Args:
        user_prompt: The user's raw description of the video they want.
        opencode_model: Opencode model to use.
        timeout_sec: Timeout for the Opencode call.

    Returns:
        Structured VideoBrief.
    """
    logger.info("Designing video spec from prompt: %s", user_prompt[:100])

    system_prompt = _build_spec_prompt(user_prompt)

    # Write prompt to temp file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        encoding="utf-8",
        delete=False,
        prefix="video_spec_",
    ) as tf:
        tf.write(system_prompt)
        prompt_path = Path(tf.name)

    try:
        stdout = await _call_opencode(prompt_path, opencode_model, timeout_sec)
        brief = _parse_video_brief(stdout)
    except Exception:
        logger.exception("Spec design failed, using default brief")
        brief = _fallback_brief(user_prompt)
    finally:
        try:
            prompt_path.unlink(missing_ok=True)
        except Exception:
            pass

    return brief


def _build_spec_prompt(user_prompt: str) -> str:
    """Build the spec designer system prompt."""
    return f"""You are a creative video spec designer. Your job is to design a marketing video based on the user's description.

## User's Request
{user_prompt}

## Your Task
1. Ask yourself: what's the product, the audience, the goal?
2. Design 3-8 scenes, each with text, animation, and timing
3. Choose a visual style (colors, tone, font)
4. Write a compelling CTA

## Output Format
At the END of your response, output EXACTLY this JSON block:

```json
{{
  "brand_name": "Brand Name",
  "product_name": "Product Name",
  "tagline": "Short tagline",
  "tone": "professional|playful|urgent|luxury|minimalist",
  "style": "modern|corporate|bold|elegant|tech",
  "primary_color": "#HEX",
  "secondary_color": "#HEX",
  "background_color": "#HEX",
  "headline": "Main headline text",
  "value_prop": "Core value proposition",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "cta_text": "Call to action",
  "duration_sec": 30,
  "aspect_ratio": "16:9",
  "scenes": [
    {{
      "index": 0,
      "text": "Scene text",
      "animation_type": "fade_in",
      "duration_sec": 4.0,
      "background_color": "#1a1a2e",
      "text_color": "#ffffff"
    }}
  ]
}}
```

Available animation types: fade_in, slide_left, slide_right, slide_up, scale_up, typewriter, bounce, rotate_in

Be creative. The JSON MUST be valid. Output ONLY the JSON after your brief analysis.
"""


async def _call_opencode(
    prompt_path: Path,
    model: str,
    timeout_sec: int,
) -> str:
    """Call Opencode CLI. Pattern from proven transcript-to-study-pipeline + meta_forge."""
    import shutil

    # Windows: find .cmd first (proven pattern from transcript-to-study-pipeline/config.py)
    opencode_bin = (
        shutil.which("opencode.cmd")
        or shutil.which("opencode")
    )
    if opencode_bin is None:
        raise RuntimeError("opencode CLI not found on PATH")

    # Inline message BEFORE --file (proven pattern from meta_forge.py)
    cmd = [
        opencode_bin, "run",
        "--model", model,
        "--dangerously-skip-permissions",
        "Design a video brief from the attached spec. Output the JSON at the end.",
        "--file", str(prompt_path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_sec
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f"Opencode timed out after {timeout_sec}s")

    return stdout_b.decode("utf-8", errors="replace")


def _parse_video_brief(stdout: str) -> VideoBrief:
    """Parse JSON from Opencode output."""
    import re

    # Find JSON block
    json_match = re.search(r'\{[\s\S]*"brand_name"[\s\S]*\}', stdout)
    if not json_match:
        json_match = re.search(r'\{[\s\S]*\}', stdout)

    if json_match:
        try:
            data = json_mod.loads(json_match.group(0))
            return _dict_to_brief(data)
        except json_mod.JSONDecodeError:
            pass

    return _fallback_brief("")


def _dict_to_brief(data: dict) -> VideoBrief:
    """Convert parsed dict to VideoBrief."""
    brief = VideoBrief(
        brand_name=data.get("brand_name", ""),
        product_name=data.get("product_name", ""),
        tagline=data.get("tagline", ""),
        tone=data.get("tone", "professional"),
        style=data.get("style", "modern"),
        primary_color=data.get("primary_color", "#6C63FF"),
        secondary_color=data.get("secondary_color", "#FF6584"),
        background_color=data.get("background_color", "#1a1a2e"),
        headline=data.get("headline", ""),
        value_prop=data.get("value_prop", ""),
        key_points=data.get("key_points", []),
        cta_text=data.get("cta_text", "Learn More"),
        cta_url=data.get("cta_url", ""),
        duration_sec=float(data.get("duration_sec", 30)),
        aspect_ratio=data.get("aspect_ratio", "16:9"),
        output_name=data.get("brand_name", "video").lower().replace(" ", "_"),
    )

    for scene_data in data.get("scenes", []):
        brief.scenes.append(Scene(
            index=scene_data.get("index", len(brief.scenes)),
            text=scene_data.get("text", ""),
            animation_type=scene_data.get("animation_type", "fade_in"),
            duration_sec=float(scene_data.get("duration_sec", 3.0)),
            background_color=scene_data.get("background_color", "#1a1a2e"),
            text_color=scene_data.get("text_color", "#ffffff"),
            font_size=scene_data.get("font_size", "48px"),
        ))

    return brief


def _fallback_brief(user_prompt: str) -> VideoBrief:
    """Fallback brief when LLM parsing fails."""
    return VideoBrief(
        brand_name="Product",
        headline=user_prompt[:100] if user_prompt else "Introducing Our Product",
        value_prop="The solution you've been waiting for",
        key_points=["Powerful features", "Easy to use", "Amazing results"],
        scenes=[
            Scene(index=0, text="Introducing...", animation_type="fade_in", duration_sec=2.0),
            Scene(index=1, text="The Future of [Product]", animation_type="slide_up", duration_sec=4.0),
            Scene(index=2, text="Get Started Today", animation_type="scale_up", duration_sec=3.0),
        ],
    )
