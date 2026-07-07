"""Marketing Video Harness — Data Schema & Configuration.

Defines the VideoBrief spec, render settings, and template registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# --- Video Spec Schema ---

@dataclass
class Scene:
    """A single scene in the video."""
    index: int = 0
    text: str = ""
    animation_type: str = "fade_in"  # fade_in, slide_left, scale_up, typewriter, bounce
    duration_sec: float = 3.0
    background_color: str = "#1a1a2e"
    text_color: str = "#ffffff"
    font_size: str = "48px"
    overlay_image: str = ""  # optional image URL


@dataclass
class VideoBrief:
    """Structured creative brief for video generation."""
    # Identity
    brand_name: str = ""
    product_name: str = ""
    tagline: str = ""

    # Creative direction
    tone: str = "professional"  # professional, playful, urgent, luxury, minimalist
    style: str = "modern"  # modern, corporate, bold, elegant, tech
    primary_color: str = "#6C63FF"
    secondary_color: str = "#FF6584"
    background_color: str = "#1a1a2e"
    font_family: str = "Inter, sans-serif"

    # Content
    headline: str = ""
    value_prop: str = ""
    key_points: list[str] = field(default_factory=list)
    cta_text: str = "Learn More"
    cta_url: str = ""

    # Scenes (auto-generated if empty)
    scenes: list[Scene] = field(default_factory=list)

    # Video settings
    duration_sec: float = 30.0
    aspect_ratio: str = "16:9"  # 16:9, 9:16, 1:1, 4:5
    fps: int = 30

    # Output
    output_name: str = ""
    campaign_name: str = ""


@dataclass
class RenderConfig:
    """Video render configuration."""
    width: int = 1920
    height: int = 1080
    fps: int = 30
    video_bitrate: str = "5000k"
    audio_bitrate: str = "192k"
    codec: str = "libx264"
    preset: str = "medium"  # ultrafast, fast, medium, slow
    format: str = "mp4"  # mp4, gif, webm
    crf: int = 23  # quality (lower = better, 18-28)
    pix_fmt: str = "yuv420p"


@dataclass
class BatchVariant:
    """A single variant in a batch run."""
    variant_id: str = ""
    aspect_ratio: str = "16:9"
    duration_sec: float = 30.0
    cta_text: str = ""
    primary_color: str = ""
    headline: str = ""


# --- Template Registry ---

TEMPLATE_REGISTRY: dict[str, dict] = {
    "product_launch": {
        "name": "Product Launch",
        "description": "Animated product showcase with feature highlights",
        "file": "templates/product_launch.html",
        "default_duration": 30,
        "has_scenes": True,
    },
    "testimonial": {
        "name": "Testimonial / Social Proof",
        "description": "Customer quote with logo and rating",
        "file": "templates/testimonial.html",
        "default_duration": 15,
        "has_scenes": False,
    },
    "explainer": {
        "name": "Explainer / How It Works",
        "description": "Problem -> Solution animation",
        "file": "templates/explainer.html",
        "default_duration": 45,
        "has_scenes": True,
    },
    "social_ad": {
        "name": "Social Media Ad",
        "description": "Short-form vertical ad for TikTok/Reels/Shorts",
        "file": "templates/social_ad.html",
        "default_duration": 15,
        "has_scenes": False,
    },
    "pricing_promo": {
        "name": "Pricing / Offer Promo",
        "description": "Pricing table with countdown urgency",
        "file": "templates/pricing_promo.html",
        "default_duration": 20,
        "has_scenes": False,
    },
}

ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
}


def get_render_config(brief: VideoBrief) -> RenderConfig:
    """Derive render config from a video brief."""
    width, height = ASPECT_RATIOS.get(brief.aspect_ratio, (1920, 1080))
    return RenderConfig(
        width=width,
        height=height,
        fps=brief.fps,
    )
