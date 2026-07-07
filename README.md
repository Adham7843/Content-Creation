# Content-Creation

**The everything-content repo.** Templates, video pipelines, script generators, social media engines, and more — all in one place.

## What's Inside

| Area | Description |
|------|-------------|
| `brands/` | Per-brand content configs, templates, and assets (voice, style, overrides) |
| `harnesses/` | Production-ready video & content pipelines (marketing videos, meme videos) |
| `agents/` | Opencode agents for content generation & management |
| `templates/` | Global default content templates (video, social, blog, email, ad copy, scripts) |
| `scripts/` | CLI tools for content creation workflows |
| `config/` | Shared configuration for all tools |
| `docs/` | Usage guides, style guides, best practices |

## Harnesses

### Marketing Video Harness
5-stage pipeline: prompt → spec → HTML → render MP4/GIF → batch variants → export.
```bash
cd harnesses/marketing-video-harness
python pipeline.py "Create a 30s product launch video" --batch 6
```

### Meme Video Harness
5-stage pipeline: source → AI clip extraction → meme effects → batch styles → export.
```bash
cd harnesses/meme-video-harness
python pipeline.py "https://youtube.com/watch?v=VIDEO" --style brainrot --clips 5
```

## Templates

| Category | Path | Contents |
|----------|------|----------|
| Video Scripts | `templates/video/` | Script structures for promos, tutorials, testimonials |
| Social Media | `templates/social/` | Posts for Twitter/X, LinkedIn, Instagram, TikTok |
| Blog | `templates/blog/` | Blog post frameworks, SEO outlines |
| Email | `templates/email/` | Marketing emails, newsletters, drip campaigns |
| Ad Copy | `templates/ad-copy/` | Facebook Ads, Google Ads, native ads |
| Scripts | `templates/script/` | Video scripts, podcast scripts, webinar scripts |

## Brands

Each brand (client/project) gets its own directory under `brands/`:

```
brands/your-brand/
├── brand.yaml          ← Voice, colors, content config, harness overrides
├── templates/          ← Brand-specific templates (override global ones)
├── agents/             ← Brand-specific agent configs
├── assets/             ← Logos, fonts, brand assets
├── harnesses/          ← Brand-specific harness configs
└── output/             ← Generated content for this brand
```

Template resolution: brand overrides first (`brands/*/templates/`), then global (`templates/`).

```bash
# Create a new brand
Copy-Item -Path brands/_template -Destination brands/my-client -Recurse
# Then edit brands/my-client/brand.yaml
```

## Quick Start

```bash
# Create a marketing video
python harnesses/marketing-video-harness/pipeline.py "Explain our SaaS product in 30s"

# Create a meme video from a YouTube link
python harnesses/meme-video-harness/pipeline.py "https://youtube.com/watch?v=dQw4w9WgXcQ" --style sigma

# Use an agent (if Opencode is configured)
opencode --agent content-video-producer "Create a testimonial video for our new feature"
```

## Business Context

This repo is one of many businesses under `SAAS_Businesses/`. It focuses exclusively on **content creation** — from video production to copywriting to social media management. Every tool and template here is designed to be deployed to client projects via the PROJECTOR manifest system.

See [PROJECTOR.md](./PROJECTOR.md) for deployment instructions.
