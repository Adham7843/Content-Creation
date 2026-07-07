# Content-Creation Architecture

## Directory Layout

```
Content-Creation/
├── brands/                     ← Per-brand content configurations
│   └── _template/              → Brand template: brand.yaml, templates/, assets/, agents/
├── harnesses/                  ← Standalone content pipelines (copied from mothra-harnesses)
│   ├── marketing-video-harness/  → 5-stage: prompt → spec → HTML → render → batch → export
│   └── meme-video-harness/       → 5-stage: source → clip → meme → batch → export
├── agents/                     ← Opencode agents for content generation
│   └── _template/              → Template for new content agents
├── templates/                  ← Global default content blueprints
│   ├── video/                  → Script structures, storyboards, shot lists
│   ├── social/                 → Platform-specific post templates
│   ├── blog/                   → Blog post frameworks, SEO outlines
│   ├── email/                  → Email marketing templates
│   ├── ad-copy/               → Ad copy frameworks
│   └── script/                 → Video/podcast/webinar scripts
├── scripts/                    ← CLI utilities for content workflows
├── config/                     ← Shared configuration
├── data/                       ← Sample data, reference materials
├── docs/                       ← Documentation, style guides
├── examples/                   ← Usage examples
├── output/                     ← Generated content (gitignored)
├── tests/                      ← Test suite
├── opencode.json              ← Master agent configuration
├── project-manifest.json       ← PROJECTOR deploy manifest
├── PROJECTOR.md               ← Deployment documentation
├── AGENT.md                    ← Master agent prompt
├── ARCHITECTURE.md             ← This file
├── README.md                   ← Entry point
├── .gitignore
└── .env.example
```

## Design Principles

1. **Brands are first-class** — Each brand/client has its own directory under `brands/` with brand.yaml (voice, visual identity, config), brand-specific templates, assets, and output. Brands override global defaults.

2. **Harnesses are standalone** — Each harness in `harnesses/` is a complete, self-contained pipeline with its own README, tests, and opencode.json. They can be used independently or orchestrated from the root.

3. **Templates cascade** — Template resolution: `brands/[brand]/templates/` first, then `templates/` as fallback. Brand templates override global ones.

4. **Agents extend the system** — Opencode agents in `agents/` provide LLM-powered interfaces to the harnesses and templates. They read `AGENT.md` at the root for behavior and check `brands/` for brand context.

5. **PROJECTOR-deployable** — The entire Content-Creation system can be deployed to any client project via `project-manifest.json` and the deploy script (from SaaS-Security-Auditor's PROJECTOR system).

## External Dependencies

| Tool | Location | Used By |
|------|----------|---------|
| opensource-clipping | `F:/Notes/Tools/opensource-clipping/` | meme-video-harness |
| brainrotbot | External | meme-video-harness |
| FFmpeg | System PATH | Both video harnesses |
| Playwright | pip | marketing-video-harness |
| Opencode CLI | System | All AI stages |

## Adding a New Harness

```bash
# Copy from mothra-harnesses output
cp -r ../mothra-harnesses/output/new-harness harnesses/
# Update opencode.json with new agent
# Update project-manifest.json
```

## Adding a New Template

```bash
# Create the template file
New-Item -Path templates/video/my-template.md
# Follow the frontmatter convention (see existing templates)
```
