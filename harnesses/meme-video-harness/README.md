# Meme Video Harness

Generate viral meme videos from any content (YouTube, Reddit, text).
Wraps opensource-clipping + brainrotbot for AI-powered viral clip extraction.

## Agent Manager

**Agent:** `meme-video-manager`

## Quick Start

```bash
python pipeline.py "https://youtube.com/watch?v=VIDEO" --style brainrot --clips 5
```

## Meme Styles (7)

brainrot | sigma | corporate_meme | tech_bro | motivational | cringe | dark_humor

## Architecture

```
pipeline.py         # Orchestrator
config.py           # 7 MemeStyle presets + tool paths
stage1_source.py    # Content fetcher (YouTube, Reddit, text)
stage2_clip.py      # opensource-clipping subprocess
stage3_meme.py      # FFmpeg effects + meme overlays
stage4_batch.py     # 1 source -> N styles
stage5_export.py    # Organize output
```

## Tools Used (at F:/Notes/Tools/)

- `opensource-clipping/` — AI auto-clipper (Whisper + Gemini + FFmpeg)
- `brainrotbot/` — Reddit meme content scraper
- FFmpeg — Video encoding + effects
