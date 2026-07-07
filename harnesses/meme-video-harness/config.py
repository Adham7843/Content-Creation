"""Meme Video Harness — Config & Schema.

Wraps tools at F:/Notes/Tools/ for viral meme video generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Tool paths ────────────────────────────────────────────────
TOOLS_ROOT = Path("F:/Notes/Tools")
OPENSOURCE_CLIPPING = TOOLS_ROOT / "opensource-clipping"
BRAINROTBOT = TOOLS_ROOT / "brainrotbot"

# Try to find FFmpeg
import shutil as _shutil
FFMPEG_BIN = (
    _shutil.which("ffmpeg")
    or _shutil.which("ffmpeg.exe")
    or ""
)


# ── Meme styles ───────────────────────────────────────────────
@dataclass
class MemeStyle:
    """A meme video style preset."""
    name: str
    description: str
    vibe: str  # brainrot, sigma, corporate, etc.
    caption_style: str  # all_caps, lowercase, mixed
    text_color: str = "#FFFFFF"
    text_stroke: str = "#000000"
    bgm_mood: str = "upbeat"  # chill, epic, upbeat, sad, suspense
    font_style: str = "DEFAULT"  # DEFAULT, STORYTELLER, HORMOZI, CINEMATIC
    effects: list[str] = field(default_factory=list)  # glitch, zoom, shake, etc.
    hook_type: str = "v2"  # v1 (simple), v2 (multi-micro-hook)
    emoji_density: str = "medium"  # low, medium, high


MEME_STYLES: dict[str, MemeStyle] = {
    "brainrot": MemeStyle(
        name="Brainrot",
        description="Maximum attention — fast cuts, loud sounds, chaotic energy. TikTok brainrot aesthetic.",
        vibe="brainrot",
        caption_style="all_caps",
        text_color="#FFFF00",
        text_stroke="#FF0000",
        bgm_mood="upbeat",
        font_style="DEFAULT",
        effects=["glitch", "shake", "zoom"],
        hook_type="v2",
        emoji_density="high",
    ),
    "sigma": MemeStyle(
        name="Sigma Grindset",
        description="Dark, intense, motivational. Patrick Bateman vibes. Black and white with red accents.",
        vibe="sigma",
        caption_style="all_caps",
        text_color="#FF0000",
        text_stroke="#000000",
        bgm_mood="epic",
        font_style="CINEMATIC",
        effects=["shake", "glitch"],
        hook_type="v2",
        emoji_density="low",
    ),
    "corporate_meme": MemeStyle(
        name="Corporate Meme",
        description="That one coworker who sends memes in #random. Clean but unhinged.",
        vibe="corporate",
        caption_style="mixed",
        text_color="#FFFFFF",
        text_stroke="#333333",
        bgm_mood="chill",
        font_style="STORYTELLER",
        effects=[],
        hook_type="v1",
        emoji_density="medium",
    ),
    "tech_bro": MemeStyle(
        name="Tech Bro",
        description="Disrupt this. Scale that. AI everything. Neon colors, fast transitions.",
        vibe="tech",
        caption_style="mixed",
        text_color="#00FF00",
        text_stroke="#000000",
        bgm_mood="upbeat",
        font_style="HORMOZI",
        effects=["glitch", "zoom"],
        hook_type="v2",
        emoji_density="medium",
    ),
    "motivational": MemeStyle(
        name="Motivational",
        description="INSPIRING. CINEMATIC. YOU CAN DO IT. Orchestra swells.",
        vibe="motivational",
        caption_style="all_caps",
        text_color="#FFFFFF",
        text_stroke="#000000",
        bgm_mood="epic",
        font_style="CINEMATIC",
        effects=[],
        hook_type="v1",
        emoji_density="low",
    ),
    "cringe": MemeStyle(
        name="Cringe",
        description="So bad it's good. Comic Sans energy. Intentionally low quality.",
        vibe="cringe",
        caption_style="mixed",
        text_color="#FF00FF",
        text_stroke="#FFFF00",
        bgm_mood="sad",
        font_style="DEFAULT",
        effects=["shake"],
        hook_type="v2",
        emoji_density="high",
    ),
    "dark_humor": MemeStyle(
        name="Dark Humor",
        description="Edgy. Ironic. Don't show your mom. Monochrome with red highlights.",
        vibe="dark",
        caption_style="lowercase",
        text_color="#888888",
        text_stroke="#000000",
        bgm_mood="suspense",
        font_style="STORYTELLER",
        effects=["glitch"],
        hook_type="v1",
        emoji_density="low",
    ),
}


# ── Config dataclass ──────────────────────────────────────────
@dataclass
class MemeConfig:
    """Runtime config for meme video generation."""
    # Source
    source_url: str = ""
    source_type: str = "youtube"  # youtube, tiktok, instagram, reddit, text

    # Style
    meme_style: str = "brainrot"
    num_clips: int = 5
    aspect_ratio: str = "9:16"  # 9:16 = TikTok, 16:9 = YouTube, 1:1 = Instagram

    # Rendering
    with_hook: bool = True
    with_subs: bool = True
    with_bgm: bool = True
    with_broll: bool = False
    face_detector: str = "mediapipe"  # mediapipe or yolo

    # Output
    output_dir: Path = Path("output/clips")
    campaign_name: str = ""

    # Tools
    ffmpeg_bin: str = field(default_factory=lambda: FFMPEG_BIN)
    clipping_tool: Path = OPENSOURCE_CLIPPING
    meme_tool: Path = BRAINROTBOT
