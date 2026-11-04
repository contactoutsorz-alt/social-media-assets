#!/usr/bin/env python3
"""Publish the raster slides contained in the two JobSultan infographic ZIPs."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "jobsultan" / "infographics"
SOURCES = {
    "circular": BASE / "Job Sultan — Circular Infographic LinkedIn Post.zip",
    "roadmap": BASE / "Job Sultan — Two-Column Roadmap Infographics (31 Slides).zip",
}
OUT = BASE / "published"
ALLOWED = {".png", ".jpg", ".jpeg", ".webp"}

def safe_name(name):
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", PurePosixPath(name).stem).strip("-._")
    suffix = PurePosixPath(name).suffix.lower()
    return stem[:100] + suffix

manifest = {}
for kind, archive in SOURCES.items():
    if not archive.is_file():
        raise SystemExit(f"Missing source archive: {archive}")
    destination = OUT / kind
    destination.mkdir(parents=True, exist_ok=True)
    for old in destination.iterdir():
        if old.is_file():
            old.unlink()
    names = set()
    with ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            member = PurePosixPath(info.filename)
            if member.suffix.lower() not in ALLOWED:
                continue
            if any(part in ("..", "") for part in member.parts):
                raise SystemExit(f"Unsafe archive member: {info.filename}")
            filename = safe_name(info.filename)
            if filename in names:
                raise SystemExit(f"Duplicate extracted filename in {kind}: {filename}")
            names.add(filename)
            target = destination / filename
            with zf.open(info) as src, target.open("wb") as dst:
                dst.write(src.read())
    files = sorted(p.name for p in destination.iterdir() if p.is_file())
    if not files:
        raise SystemExit(f"No PNG/JPG/WebP slides found in {archive.name}")
    manifest[kind] = files

(BASE / "published" / "manifest.json").write_text(
    json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({k: len(v) for k, v in manifest.items()}, indent=2))
