"""Tests for meme-video-harness."""

from __future__ import annotations

import unittest
from pathlib import Path

from config import (
    MemeConfig,
    MemeStyle,
    MEME_STYLES,
    TOOLS_ROOT,
    OPENSOURCE_CLIPPING,
    BRAINROTBOT,
    FFMPEG_BIN,
)
from stage1_source import _detect_source_type
from stage4_batch import generate_batch


class TestMemeStyles(unittest.TestCase):
    def test_all_styles_defined(self) -> None:
        assert len(MEME_STYLES) == 7
        assert "brainrot" in MEME_STYLES
        assert "sigma" in MEME_STYLES
        assert "corporate_meme" in MEME_STYLES
        assert "tech_bro" in MEME_STYLES

    def test_style_has_fields(self) -> None:
        for name, style in MEME_STYLES.items():
            assert style.name, f"{name} has no name"
            assert style.vibe, f"{name} has no vibe"
            assert style.caption_style in ("all_caps", "lowercase", "mixed"), f"{name} bad caption_style"
            assert style.hook_type in ("v1", "v2"), f"{name} bad hook_type"

    def test_brainrot_style(self) -> None:
        br = MEME_STYLES["brainrot"]
        assert br.vibe == "brainrot"
        assert br.caption_style == "all_caps"
        assert "glitch" in br.effects
        assert br.emoji_density == "high"

    def test_sigma_style(self) -> None:
        sg = MEME_STYLES["sigma"]
        assert sg.vibe == "sigma"
        assert sg.text_color == "#FF0000"
        assert sg.bgm_mood == "epic"


class TestConfig(unittest.TestCase):
    def test_default_config(self) -> None:
        cfg = MemeConfig()
        assert cfg.meme_style == "brainrot"
        assert cfg.num_clips == 5
        assert cfg.aspect_ratio == "9:16"

    def test_tool_paths_exist(self) -> None:
        # Tools should be at F:/Notes/Tools/
        assert TOOLS_ROOT.exists(), f"Tools root not found: {TOOLS_ROOT}"
        # Note: tools may not exist if not cloned
        # These are soft checks

    def test_ffmpeg_path(self) -> None:
        # FFmpeg may or may not be installed
        cfg = MemeConfig()
        assert isinstance(cfg.ffmpeg_bin, str)


class TestSourceDetection(unittest.TestCase):
    def test_youtube(self) -> None:
        assert _detect_source_type("https://youtube.com/watch?v=abc") == "youtube"
        assert _detect_source_type("https://youtu.be/abc") == "youtube"

    def test_reddit(self) -> None:
        assert _detect_source_type("https://reddit.com/r/python/comments/abc") == "reddit"

    def test_tiktok(self) -> None:
        assert _detect_source_type("https://tiktok.com/@user/video/123") == "tiktok"

    def test_text(self) -> None:
        assert _detect_source_type("This is just some text") == "text"


class TestBatch(unittest.TestCase):
    def test_generate_batch(self) -> None:
        cfg = MemeConfig(source_url="https://example.com")
        import asyncio
        configs = asyncio.run(generate_batch(cfg, ["brainrot", "sigma"]))
        assert len(configs) == 2
        assert configs[0].meme_style == "brainrot"
        assert configs[1].meme_style == "sigma"

    def test_batch_preserves_url(self) -> None:
        cfg = MemeConfig(source_url="https://test.com/video", num_clips=7)
        import asyncio
        configs = asyncio.run(generate_batch(cfg, ["tech_bro"]))
        assert configs[0].source_url == "https://test.com/video"
        assert configs[0].num_clips == 7


if __name__ == "__main__":
    unittest.main()
