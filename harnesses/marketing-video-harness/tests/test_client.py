"""Tests for marketing-video-harness."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from config import (
    VideoBrief,
    Scene,
    RenderConfig,
    BatchVariant,
    get_render_config,
    ASPECT_RATIOS,
    TEMPLATE_REGISTRY,
)
from stage4_batch import _build_variants, apply_variant, COLOR_SCHEMES


class TestVideoBrief(unittest.TestCase):
    def test_default_brief(self) -> None:
        brief = VideoBrief()
        assert brief.tone == "professional"
        assert brief.aspect_ratio == "16:9"
        assert brief.fps == 30
        assert brief.scenes == []

    def test_brief_with_scenes(self) -> None:
        brief = VideoBrief(
            brand_name="TestBrand",
            headline="Amazing Product",
            scenes=[
                Scene(index=0, text="Scene 1", animation_type="fade_in"),
                Scene(index=1, text="Scene 2", animation_type="slide_up"),
            ],
        )
        assert len(brief.scenes) == 2
        assert brief.scenes[0].animation_type == "fade_in"
        assert brief.scenes[1].text == "Scene 2"

    def test_brief_to_json_roundtrip(self) -> None:
        brief = VideoBrief(
            brand_name="Slack",
            headline="Where Work Happens",
            key_points=["Channels", "Integrations"],
            scenes=[Scene(index=0, text="Hello", animation_type="fade_in")],
        )
        raw = {
            "brand_name": brief.brand_name,
            "headline": brief.headline,
            "key_points": brief.key_points,
            "tone": brief.tone,
            "style": brief.style,
            "primary_color": brief.primary_color,
            "secondary_color": brief.secondary_color,
            "background_color": brief.background_color,
            "font_family": brief.font_family,
            "cta_text": brief.cta_text,
            "duration_sec": brief.duration_sec,
            "aspect_ratio": brief.aspect_ratio,
            "scenes": [
                {"index": 0, "text": "Hello", "animation_type": "fade_in",
                 "duration_sec": 3.0, "background_color": "#1a1a2e",
                 "text_color": "#ffffff", "font_size": "48px", "overlay_image": ""}
            ],
        }
        json_str = json.dumps(raw)
        parsed = json.loads(json_str)
        assert parsed["brand_name"] == "Slack"
        assert len(parsed["scenes"]) == 1


class TestRenderConfig(unittest.TestCase):
    def test_default_config(self) -> None:
        cfg = RenderConfig()
        assert cfg.width == 1920
        assert cfg.height == 1080
        assert cfg.fps == 30
        assert cfg.format == "mp4"

    def test_get_render_config(self) -> None:
        brief = VideoBrief(aspect_ratio="9:16")
        cfg = get_render_config(brief)
        assert cfg.width == 1080
        assert cfg.height == 1920

    def test_square_config(self) -> None:
        brief = VideoBrief(aspect_ratio="1:1")
        cfg = get_render_config(brief)
        assert cfg.width == 1080
        assert cfg.height == 1080


class TestBatchVariants(unittest.TestCase):
    def test_build_variants_count(self) -> None:
        brief = VideoBrief(brand_name="Test")
        variants = _build_variants(brief, 6)
        assert len(variants) == 6

    def test_variants_have_different_ctas(self) -> None:
        brief = VideoBrief(brand_name="Test")
        variants = _build_variants(brief, 8)
        ctas = {v.cta_text for v in variants}
        assert len(ctas) > 1  # variety

    def test_apply_variant_changes_brief(self) -> None:
        brief = VideoBrief(
            brand_name="Test",
            aspect_ratio="16:9",
            duration_sec=30,
            cta_text="Original CTA",
            scenes=[Scene(index=0, text="S1", duration_sec=10.0)],
        )
        variant = BatchVariant(
            variant_id="9x16_15s",
            aspect_ratio="9:16",
            duration_sec=15,
            cta_text="New CTA",
            primary_color="#FF0000",
        )
        new_brief = apply_variant(brief, variant)
        assert new_brief.aspect_ratio == "9:16"
        assert new_brief.duration_sec == 15
        assert new_brief.cta_text == "New CTA"
        assert new_brief.primary_color == "#FF0000"

    def test_apply_variant_adjusts_scene_durations(self) -> None:
        brief = VideoBrief(
            scenes=[Scene(index=0, duration_sec=10.0), Scene(index=1, duration_sec=10.0)],
            duration_sec=30,
        )
        variant = BatchVariant(variant_id="test", duration_sec=15.0)
        new_brief = apply_variant(brief, variant)
        for scene in new_brief.scenes:
            assert scene.duration_sec <= 15.0


class TestTemplateRegistry(unittest.TestCase):
    def test_registry_has_templates(self) -> None:
        assert "product_launch" in TEMPLATE_REGISTRY
        assert "social_ad" in TEMPLATE_REGISTRY
        assert "explainer" in TEMPLATE_REGISTRY

    def test_template_files_exist(self) -> None:
        harness_dir = Path(__file__).parent.parent
        for name, info in TEMPLATE_REGISTRY.items():
            tmpl_path = harness_dir / info["file"]
            assert tmpl_path.exists(), f"Template {name} not found at {tmpl_path}"

    def test_color_schemes(self) -> None:
        assert len(COLOR_SCHEMES) == 6
        for primary, secondary in COLOR_SCHEMES:
            assert primary.startswith("#")
            assert secondary.startswith("#")


class TestAspectRatios(unittest.TestCase):
    def test_known_ratios(self) -> None:
        assert ("16:9" in ASPECT_RATIOS)
        assert ("9:16" in ASPECT_RATIOS)
        assert ("1:1" in ASPECT_RATIOS)
        assert ASPECT_RATIOS["16:9"] == (1920, 1080)
        assert ASPECT_RATIOS["9:16"] == (1080, 1920)


if __name__ == "__main__":
    unittest.main()
