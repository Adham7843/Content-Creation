# Video Script Templates

Blueprint frameworks for video content. Copy the template you need and fill in the placeholders.

## Available Templates

| Template | Best For |
|----------|----------|
| `product-launch.md` | Launching a new product or feature |
| `explainer.md` | Explaining a concept or how something works |
| `testimonial.md` | Customer success story / testimonial |
| `tutorial.md` | Step-by-step how-to guide |
| `social-ad.md` | Short-form ad (TikTok, Reels, Shorts) |
| `pricing-promo.md` | Pricing / offer promotion |
| `behind-the-scenes.md` | Building trust with BTS content |
| `thought-leadership.md` | Industry insights / expert takes |

## Template Format

Each template uses this structure:

```markdown
---
type: [video type]
duration: [target length]
platform: [YouTube/TikTok/LinkedIn/etc]
tone: [professional/casual/humorous/urgent]
---

## Hook (0-5s)
[Grab attention]

## Problem (5-15s)
[State the pain point]

## Solution (15-45s)
[Present your solution]

## Proof (45-60s)
[Social proof, stats, testimonials]

## CTA (60-75s)
[Call to action]
```

## Usage with Content Agent

```bash
opencode --agent content-writer "Write a product launch script for our new AI tool, 60 seconds, professional tone"
```
