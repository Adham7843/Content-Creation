# Brand Template

Copy this folder to create a new brand:

```bash
# PowerShell
Copy-Item -Path brands/_template -Destination brands/your-brand -Recurse

# Then edit brands/your-brand/brand.yaml
# And customize brands/your-brand/templates/
```

## Structure

```
brands/your-brand/
├── brand.yaml          ← Brand identity, voice, content config
├── templates/          ← Brand-specific template overrides
│   ├── video/
│   ├── social/
│   ├── blog/
│   ├── email/
│   ├── ad-copy/
│   └── script/
├── agents/             ← Brand-specific agent configs
├── harnesses/          ← Brand-specific harness overrides
├── assets/             ← Logos, fonts, brand assets
└── output/             ← Generated content for this brand
```

Template resolution order:
1. `brands/brand-name/templates/[category]/` (brand-specific first)
2. `templates/[category]/` (global fallback)
