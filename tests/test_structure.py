"""Test that Content-Creation structure is intact."""

from pathlib import Path


ROOT = Path(__file__).parent.parent


def test_root_exists():
    assert ROOT.exists()
    assert ROOT.is_dir()


def test_core_files_exist():
    """Core documentation and config files must be present."""
    files = [
        "README.md",
        "AGENT.md",
        "ARCHITECTURE.md",
        "opencode.json",
        "project-manifest.json",
        "PROJECTOR.md",
        ".gitignore",
        ".env.example",
    ]
    for f in files:
        assert (ROOT / f).exists(), f"Missing: {f}"


def test_directories_exist():
    """All required directories must be present."""
    dirs = [
        "brands/_template",
        "harnesses",
        "agents/_template",
        "templates/video",
        "templates/social",
        "templates/blog",
        "templates/email",
        "templates/ad-copy",
        "templates/script",
        "scripts",
        "config",
        "data",
        "docs",
        "examples",
        "output",
        "tests",
    ]
    for d in dirs:
        assert (ROOT / d).exists(), f"Missing directory: {d}"


def test_brand_template_structure():
    """Brand _template must have all required subdirs and files."""
    tmpl = ROOT / "brands" / "_template"
    assert (tmpl / "brand.yaml").exists(), "Missing brand.yaml"
    assert (tmpl / "README.md").exists(), "Missing brand README.md"
    for td in ["templates/video", "templates/social", "templates/blog",
               "templates/email", "templates/ad-copy", "templates/script",
               "agents", "harnesses", "assets", "output"]:
        assert (tmpl / td).exists(), f"Missing brand template dir: {td}"


def test_brand_yaml_content():
    """brand.yaml must have required fields."""
    import yaml
    with open(ROOT / "brands" / "_template" / "brand.yaml") as f:
        brand = yaml.safe_load(f)
    assert "name" in brand
    assert "voice" in brand
    assert "visual" in brand
    assert "content_types" in brand
    assert "video" in brand.get("content_types", {})
    assert "harnesses" in brand


def test_video_harnesses_copied():
    """Both video harnesses must be copied from mothra-harnesses."""
    harnesses = [
        "marketing-video-harness",
        "meme-video-harness",
    ]
    for h in harnesses:
        harness_dir = ROOT / "harnesses" / h
        assert harness_dir.exists(), f"Missing harness: {h}"
        # Check key files exist in each harness
        key_files = ["pipeline.py", "config.py", "README.md", "AGENT.md", "META.json"]
        for kf in key_files:
            assert (harness_dir / kf).exists(), f"Missing {kf} in {h}"


def test_template_readmes():
    """Each template category should have a README."""
    template_dirs = ["video", "social", "blog", "email", "ad-copy", "script"]
    for td in template_dirs:
        assert (ROOT / "templates" / td / "README.md").exists(), f"Missing README in templates/{td}"


def test_opencode_agents():
    """opencode.json must define content agents."""
    import json
    with open(ROOT / "opencode.json") as f:
        config = json.load(f)
    agents = config.get("agents", {})
    agent_names = ["content-video-producer", "content-meme-producer", "content-writer"]
    for name in agent_names:
        assert name in agents, f"Missing agent: {name}"


def test_project_manifest():
    """project-manifest.json must be valid and reference harnesses."""
    import json
    with open(ROOT / "project-manifest.json") as f:
        manifest = json.load(f)
    assert "harnesses" in manifest
    assert "agents" in manifest
    assert "templates" in manifest
    assert len(manifest["harnesses"]) >= 2
    assert len(manifest["agents"]) >= 3
