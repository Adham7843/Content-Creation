#!/usr/bin/env python3
"""
Content-Creation Project & Brand Initializer

Creates new content projects or brands from templates.
Zero external dependencies -- stdlib only.

Usage:
    # Create a content project
    python scripts/init_content_project.py --name "my-project" --type full
    
    # Create a brand (from brands/_template/)
    python scripts/init_content_project.py --brand "client-name"
    
    # Create a brand with custom voice and color
    python scripts/init_content_project.py --brand "client-name" --voice humorous --color "#FF6600"
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


CONTENT_TYPES = {
    "video": {
        "dirs": ["scripts", "assets", "output", "versions"],
        "harnesses": ["marketing-video-harness", "meme-video-harness"],
        "description": "Video content project",
    },
    "blog": {
        "dirs": ["posts", "images", "research", "drafts", "published"],
        "harnesses": [],
        "description": "Blog content project",
    },
    "social": {
        "dirs": ["posts", "graphics", "scheduling", "analytics"],
        "harnesses": [],
        "description": "Social media content project",
    },
    "email": {
        "dirs": ["campaigns", "templates", "lists", "analytics"],
        "harnesses": [],
        "description": "Email marketing project",
    },
    "full": {
        "dirs": [
            "video/scripts",
            "video/assets",
            "video/output",
            "blog/posts",
            "blog/images",
            "social/posts",
            "social/graphics",
            "email/campaigns",
            "email/templates",
            "ad-copy/campaigns",
            "scripts/podcast",
            "assets",
            "output",
        ],
        "harnesses": ["marketing-video-harness", "meme-video-harness"],
        "description": "Full content project (all types)",
    },
}


def init_brand(name: str, voice: str, color: str, content_root: Path) -> Path:
    """Create a new brand from _template using string replacement (zero deps)."""
    template_dir = content_root / "brands" / "_template"
    if not template_dir.exists():
        print(f"Error: Brand template not found at {template_dir}")
        sys.exit(1)

    brand_dir = content_root / "brands" / name
    if brand_dir.exists():
        print(f"Error: Brand '{name}' already exists at {brand_dir}")
        sys.exit(1)

    # Copy template
    shutil.copytree(
        template_dir,
        brand_dir,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
    )
    print(f"  [OK] Copied brand template")

    # Update brand.yaml via string replacement (no YAML parser needed)
    brand_yaml_path = brand_dir / "brand.yaml"
    if brand_yaml_path.exists():
        content = brand_yaml_path.read_text(encoding="utf-8")
        content = content.replace("Your Brand Name", name)
        content = content.replace('tone: "professional"', f'tone: "{voice}"')
        if color:
            content = content.replace('primary_color: "#000000"', f'primary_color: "{color}"')
        brand_yaml_path.write_text(content, encoding="utf-8")
        print(f"  [OK] Updated brand.yaml (name={name}, voice={voice}, color={color or 'default'})")

    # Ensure .gitkeep in empty dirs
    for subdir in ["templates/video", "templates/social", "templates/blog",
                   "templates/email", "templates/ad-copy", "templates/script",
                   "agents", "harnesses", "assets", "output"]:
        d = brand_dir / subdir
        if d.exists() and not any(d.iterdir()):
            (d / ".gitkeep").write_text("")

    print(f"\n[DONE] Brand '{name}' created at {brand_dir}")
    print(f"   Voice: {voice}")
    print(f"   Color: {color or '#000000 (default)'}")
    print(f"\nNext steps:")
    print(f"   1. Edit {brand_yaml_path} with full brand details")
    print(f"   2. Add brand assets to {brand_dir / 'assets'}")
    print(f"   3. Create templates in {brand_dir / 'templates'}/[category]/")
    print(f"   4. Generate content via harnesses")
    return brand_dir


def create_project(name: str, content_type: str, parent_dir: Path) -> Path:
    """Create a new content project directory."""
    if content_type not in CONTENT_TYPES:
        print(f"Error: Unknown content type '{content_type}'")
        print(f"Available types: {', '.join(CONTENT_TYPES.keys())}")
        sys.exit(1)

    project_dir = parent_dir / name
    if project_dir.exists():
        print(f"Error: Project '{name}' already exists at {project_dir}")
        sys.exit(1)

    config = CONTENT_TYPES[content_type]
    root_dir = parent_dir.parent

    # Create directory structure
    for subdir in config["dirs"]:
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)

    for subdir in config["dirs"]:
        gitkeep = project_dir / subdir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("")

    # Copy harnesses if applicable
    harnesses_dir = project_dir / "harnesses"
    if config["harnesses"]:
        harnesses_dir.mkdir(exist_ok=True)
        for harness_name in config["harnesses"]:
            src = root_dir / "harnesses" / harness_name
            if src.exists():
                dst = harnesses_dir / harness_name
                if not dst.exists():
                    shutil.copytree(
                        src,
                        dst,
                        ignore=shutil.ignore_patterns(
                            "__pycache__", ".pytest_cache", "output"
                        ),
                    )
                    print(f"  [OK] Copied harness: {harness_name}")
                else:
                    print(f"  - Harness already exists: {harness_name}")

    # Project config
    project_config = {
        "name": name,
        "type": content_type,
        "created": datetime.now().isoformat(),
        "description": config["description"],
        "directories": config["dirs"],
        "harnesses": config["harnesses"],
    }
    (project_dir / "project.json").write_text(json.dumps(project_config, indent=2))

    readme = f"""# {name}

*{config['description']}*

Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Structure
{chr(10).join(f'- {d}/' for d in config['dirs'])}

## Quick Start
```bash
# Run a marketing video pipeline
python harnesses/marketing-video-harness/pipeline.py "Your brief here"

# Run a meme video pipeline
python harnesses/meme-video-harness/pipeline.py "https://youtube.com/..." --style brainrot
```
"""
    (project_dir / "README.md").write_text(readme)

    print(f"\n[DONE] Content project '{name}' created at {project_dir}")
    print(f"   Type: {content_type}")
    print(f"   Directories: {len(config['dirs'])}")
    print(f"   Harnesses: {len(config['harnesses'])}")
    return project_dir


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new content project or brand"
    )
    parser.add_argument(
        "--name", "-n",
        help="Project name (directory name)",
    )
    parser.add_argument(
        "--type", "-t",
        choices=list(CONTENT_TYPES.keys()),
        default="full",
        help="Content type (default: full)",
    )
    parser.add_argument(
        "--parent",
        default="projects",
        help="Parent directory under Content-Creation/ (default: projects/)",
    )
    parser.add_argument(
        "--brand", "-b",
        help="Create a new brand from _template (use instead of --name)",
    )
    parser.add_argument(
        "--voice",
        default="professional",
        choices=["professional", "casual", "humorous", "inspirational", "authoritative"],
        help="Brand voice/tone (default: professional)",
    )
    parser.add_argument(
        "--color",
        help="Brand primary color (hex, e.g., #FF6600)",
    )

    args = parser.parse_args()
    
    script_dir = Path(__file__).parent.resolve()
    content_root = script_dir.parent

    # Brand mode
    if args.brand:
        init_brand(args.brand, args.voice, args.color, content_root)
        return

    # Project mode
    if not args.name:
        parser.print_help()
        print("\nError: Either --name or --brand is required.")
        sys.exit(1)

    parent_dir = content_root / args.parent
    parent_dir.mkdir(exist_ok=True)
    create_project(args.name, args.type, parent_dir)


if __name__ == "__main__":
    main()
