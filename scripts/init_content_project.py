#!/usr/bin/env python3
"""
Content-Creation Project Initializer

Creates a new content project directory with:
- Copied template structures
- Video harness integrations
- Basic config

Usage:
    python scripts/init_content_project.py --name "my-content-project" --type video
    python scripts/init_content_project.py --name "client-blog" --type blog
"""

import argparse
import json
import os
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

    # Get the content type config
    config = CONTENT_TYPES[content_type]
    root_dir = parent_dir.parent  # Content-Creation root

    # Create directory structure
    for subdir in config["dirs"]:
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Create .gitkeep in empty dirs
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
                        ignore=shutil.ignoring_patterns(
                            "__pycache__", ".pytest_cache", "output"
                        ),
                    )
                    print(f"  ✓ Copied harness: {harness_name}")
                else:
                    print(f"  - Harness already exists: {harness_name}")

    # Create project config
    project_config = {
        "name": name,
        "type": content_type,
        "created": datetime.now().isoformat(),
        "description": config["description"],
        "directories": config["dirs"],
        "harnesses": config["harnesses"],
    }
    (project_dir / "project.json").write_text(json.dumps(project_config, indent=2))

    # Create a minimal README
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

    print(f"\n✅ Content project '{name}' created at {project_dir}")
    print(f"   Type: {content_type}")
    print(f"   Directories: {len(config['dirs'])}")
    print(f"   Harnesses: {len(config['harnesses'])}")
    return project_dir


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new content project"
    )
    parser.add_argument(
        "--name", "-n",
        required=True,
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

    args = parser.parse_args()

    # Resolve paths relative to Content-Creation root
    script_dir = Path(__file__).parent.resolve()
    content_root = script_dir.parent  # Content-Creation root
    parent_dir = content_root / args.parent
    parent_dir.mkdir(exist_ok=True)

    create_project(args.name, args.type, parent_dir)


if __name__ == "__main__":
    main()
