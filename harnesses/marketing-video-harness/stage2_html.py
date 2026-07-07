"""Stage 2: HTML Generator — VideoBrief → animated HTML/CSS.

Generates a standalone HTML file with CSS animations based on the video spec.
Includes scene transitions, text animations, CTA button, and brand styling.
"""

from __future__ import annotations

import asyncio
import json as json_mod
import logging
import tempfile
from pathlib import Path

from config import VideoBrief, Scene

logger = logging.getLogger(__name__)


async def generate_html(
    brief: VideoBrief,
    template_name: str = "product_launch",
    opencode_model: str = "opencode/deepseek-v4-flash-free",
    timeout_sec: int = 300,
) -> str:
    """Generate animated HTML from a VideoBrief.

    Args:
        brief: The structured video brief.
        template_name: Which template to base on (from TEMPLATE_REGISTRY).
        opencode_model: Opencode model for HTML generation.
        timeout_sec: Timeout.

    Returns:
        Complete HTML string with embedded CSS animations.
    """
    logger.info("Generating HTML for %s using template %s", brief.brand_name, template_name)

    # Try LLM generation first
    prompt = _build_html_prompt(brief, template_name)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", encoding="utf-8", delete=False, prefix="html_gen_"
    ) as tf:
        tf.write(prompt)
        prompt_path = Path(tf.name)

    try:
        stdout = await _call_opencode_html(prompt_path, opencode_model, timeout_sec)
        html = _extract_html(stdout)
        if html and len(html) > 200:
            return html
    except Exception:
        logger.exception("LLM HTML generation failed, using template fallback")
    finally:
        try:
            prompt_path.unlink(missing_ok=True)
        except Exception:
            pass

    return _template_fallback(brief)


def _build_html_prompt(brief: VideoBrief, template_name: str) -> str:
    """Build the HTML generation prompt."""
    scenes_json = json_mod.dumps(
        [
            {
                "index": s.index,
                "text": s.text,
                "animation": s.animation_type,
                "duration": s.duration_sec,
                "bg": s.background_color,
                "color": s.text_color,
            }
            for s in brief.scenes
        ],
        indent=2,
    )

    return f"""Generate a complete, standalone HTML file with embedded CSS animations for a marketing video.

## Video Spec
- Brand: {brief.brand_name}
- Product: {brief.product_name}
- Headline: {brief.headline}
- Value Prop: {brief.value_prop}
- Key Points: {', '.join(brief.key_points)}
- Tone: {brief.tone}
- Primary Color: {brief.primary_color}
- Secondary Color: {brief.secondary_color}
- Background: {brief.background_color}
- Font: {brief.font_family}
- CTA: {brief.cta_text}
- Aspect Ratio: {brief.aspect_ratio}
- Duration: {brief.duration_sec}s
- Scenes: {scenes_json}

## Requirements
- Single HTML file, no external dependencies
- CSS @keyframes for each animation type
- Each scene is a full-screen div that animates in/out
- Auto-advance scenes based on duration
- CTA button on the last scene
- Use viewport units (vw, vh) for responsiveness
- Background gradient using brand colors
- Smooth easing (cubic-bezier)
- Include a subtle particle or geometric background effect
- NO JavaScript frameworks — vanilla CSS + minimal JS for scene timing

## Output
Return ONLY the complete HTML. Start with <!DOCTYPE html>.
Do NOT wrap in markdown code blocks.
"""


async def _call_opencode_html(
    prompt_path: Path,
    model: str,
    timeout_sec: int,
) -> str:
    """Call Opencode for HTML generation. Pattern from proven harnesses."""
    import shutil

    opencode_bin = (
        shutil.which("opencode.cmd")
        or shutil.which("opencode")
    )
    if opencode_bin is None:
        raise RuntimeError("opencode CLI not found on PATH")

    cmd = [
        opencode_bin, "run",
        "--model", model,
        "--dangerously-skip-permissions",
        "Generate the HTML from the attached spec. Output ONLY the complete HTML file.",
        "--file", str(prompt_path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, _ = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_sec
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f"HTML generation timed out after {timeout_sec}s")

    return stdout_b.decode("utf-8", errors="replace")


def _extract_html(stdout: str) -> str:
    """Extract HTML from LLM output."""
    import re

    # Look for html blocks
    html_match = re.search(r'(<!DOCTYPE html>[\s\S]*?</html>)', stdout, re.IGNORECASE)
    if html_match:
        return html_match.group(1)

    # Try code-fenced HTML
    code_match = re.search(r'```html\s*([\s\S]*?)```', stdout)
    if code_match:
        return code_match.group(1)

    # Try any code fence
    code_match = re.search(r'```\s*([\s\S]*?)```', stdout)
    if code_match:
        content = code_match.group(1)
        if '<!DOCTYPE' in content or '<html' in content:
            return content

    return ""


def _template_fallback(brief: VideoBrief) -> str:
    """Generate HTML from built-in template when LLM fails."""
    scenes_html = ""
    total_dur = 0.0

    for i, scene in enumerate(brief.scenes):
        dur = scene.duration_sec * 1000  # ms
        delay = total_dur * 1000
        scenes_html += f"""
        <div class="scene" style="
            animation: {scene.animation_type} {dur}ms {delay}ms both;
            background: {scene.background_color};
            color: {scene.text_color};
        ">
            <h2>{scene.text}</h2>
        </div>
        """
        total_dur += scene.duration_sec

    # Add CTA scene
    cta_delay = total_dur * 1000
    scenes_html += f"""
        <div class="scene cta-scene" style="
            animation: scale_up 2000ms {cta_delay}ms both;
            background: linear-gradient(135deg, {brief.primary_color}, {brief.secondary_color});
        ">
            <h2>{brief.headline}</h2>
            <p>{brief.value_prop}</p>
            <a class="cta-button" href="{brief.cta_url or '#'}">{brief.cta_text}</a>
        </div>
    """
    total_dur += 4.0

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{brief.brand_name} - {brief.headline}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: {brief.font_family};
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    background: {brief.background_color};
}}
.scene {{
    position: absolute;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 5vw;
    opacity: 0;
}}
.scene h2 {{ font-size: 4vw; font-weight: 700; margin-bottom: 2vh; }}
.cta-scene p {{ font-size: 2vw; margin-bottom: 4vh; opacity: 0.9; }}
.cta-button {{
    display: inline-block;
    padding: 2vh 4vw;
    font-size: 2.5vw;
    font-weight: 700;
    color: {brief.primary_color};
    background: white;
    border-radius: 100px;
    text-decoration: none;
    transition: transform 0.3s;
}}
.cta-button:hover {{ transform: scale(1.05); }}

@keyframes fade_in {{
    0% {{ opacity: 0; }}
    100% {{ opacity: 1; }}
}}
@keyframes slide_up {{
    0% {{ opacity: 0; transform: translateY(60px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slide_left {{
    0% {{ opacity: 0; transform: translateX(60px); }}
    100% {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes scale_up {{
    0% {{ opacity: 0; transform: scale(0.8); }}
    100% {{ opacity: 1; transform: scale(1); }}
}}
@keyframes bounce {{
    0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
    40% {{ transform: translateY(-20px); }}
    60% {{ transform: translateY(-10px); }}
}}
@keyframes typewriter {{
    from {{ width: 0; }}
    to {{ width: 100%; }}
}}

@keyframes bgPulse {{
    0%, 100% {{ opacity: 0.03; }}
    50% {{ opacity: 0.08; }}
}}
.bg-decoration {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: radial-gradient(circle at 50% 50%, {brief.primary_color}44 0%, transparent 70%);
    animation: bgPulse 4s ease-in-out infinite;
    z-index: 0;
}}
.scene {{ z-index: 1; }}
</style>
</head>
<body>
<div class="bg-decoration"></div>
{scenes_html}
<script>
const totalDuration = {int(total_dur * 1000)};
setTimeout(() => {{ document.body.style.opacity = '0.5'; }}, totalDuration);
</script>
</body>
</html>"""
