# Marketing Video Harness

Generate marketing videos from natural language prompts. 5-stage pipeline.

## Agent Manager

**Agent:** `marketing-video-manager` — invoke with `@marketing-video-manager "your prompt"`

## Quick Start

```bash
python pipeline.py "Create a 30s product launch video for Slack" --batch 6
```

## Architecture

```
pipeline.py          # Orchestrator
config.py            # VideoBrief schema + render config + template registry
stage1_spec.py       # Prompt -> structured VideoBrief (Opencode LLM)
stage2_html.py       # VideoBrief -> animated HTML/CSS (LLM + templates)
stage3_render.py     # HTML -> MP4/GIF (Playwright frames + FFmpeg)
stage4_batch.py      # 1 spec -> N variants (colors, CTAs, ratios, durations)
stage5_export.py     # Organize + metadata.json
templates/           # HTML video templates
```

## Templates

| Template | Best For | Duration |
|----------|----------|----------|
| `product_launch` | Feature/product showcase | 30s |
| `social_ad` | TikTok/Reels/Shorts ad | 15s |
| `explainer` | Problem → solution | 45s |
| `testimonial` | Customer quote | 15s |
| `pricing_promo` | Pricing table | 20s |

## Dependencies

- Python 3.11+
- Playwright (`playwright install chromium`)
- FFmpeg (in PATH)
- Opencode CLI (for AI stages)

## Run Tests

```bash
python -m pytest tests/test_client.py -v
```
