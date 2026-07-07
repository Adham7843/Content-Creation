# PROJECTOR — Content-Creation Deployment

This repository is a **PROJECTOR-managed** business unit under `SAAS_Businesses/`. All deployable components are listed in `project-manifest.json`.

## What Deploys

| Component | Type | Deploy To |
|-----------|------|-----------|
| `brands/_template/` | Brand template | `brands/` |
| `harnesses/marketing-video-harness/` | Harness | `harnesses/` |
| `harnesses/meme-video-harness/` | Harness | `harnesses/` |
| `templates/` | Global templates | `templates/` |
| `agents/_template/` | Agent template | `agents/` |
| `config/` | Config | `config/` |
| `opencode.json` | Agent config | Root |

## Deploy to a Client Project

```bash
# Using the deploy script from SaaS-Security-Auditor
python ../SaaS-Security-Auditor/scripts/deploy_project.py \
  --manifest project-manifest.json \
  --target ../Client-Project \
  --components harnesses,templates,config
```

## External Dependencies (not deployed, must exist on target)

- FFmpeg (system PATH)
- Playwright (`pip install playwright && playwright install chromium`)
- opensource-clipping at `F:/Notes/Tools/opensource-clipping/`
- Opencode CLI

## Adding New Content to This Repo

1. Add harnesses to `harnesses/`
2. Add templates to `templates/[category]/`
3. Add agents to `agents/`
4. Update `project-manifest.json`
5. Update `opencode.json` if new agents are added
