#!/usr/bin/env python3
"""Extract the nine approved JobSultan carousel archives into public slide assets."""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAROUSELS = ROOT / "jobsultan" / "carousels"
PUBLISHED = CAROUSELS / "published"
MANIFEST = CAROUSELS / "manifest.json"
OWNER = "contactoutsorz-alt"
REPO = "social-media-assets"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def natural_key(value: str):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", value)]


def image_signature(data: bytes, suffix: str) -> bool:
    suffix = suffix.lower()
    if suffix == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in (".jpg", ".jpeg"):
        return data.startswith(b"\xff\xd8\xff")
    if suffix == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return False


def main():
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if len(manifest.get("carousels", [])) == 60 and PUBLISHED.exists():
            print("Carousel assets already extracted; nothing to do.")
            return

    archives = []
    for path in CAROUSELS.glob("*.zip"):
        match = re.search(r"Batch\s*(\d+)", path.name, re.IGNORECASE)
        if match:
            archives.append((int(match.group(1)), path))
    archives.sort(key=lambda item: item[0])
    if [number for number, _ in archives] != list(range(1, 10)):
        raise SystemExit("Expected exactly the nine numbered JobSultan carousel ZIP archives.")

    if PUBLISHED.exists():
        import shutil
        shutil.rmtree(PUBLISHED)
    PUBLISHED.mkdir(parents=True)

    carousels = []
    carousel_number = 0
    total_images = 0

    for batch_number, archive in archives:
        with zipfile.ZipFile(archive) as zf:
            bad = zf.testzip()
            if bad:
                raise SystemExit(f"ZIP CRC check failed: {archive.name}: {bad}")
            entries = [
                name for name in zf.namelist()
                if not name.endswith("/")
                and Path(name).suffix.lower() in IMAGE_EXTS
                and not any(part.startswith("__MACOSX") or part.startswith(".")
                            for part in Path(name).parts)
            ]
            entries.sort(key=natural_key)
            expected = 49 if batch_number <= 8 else 28
            if len(entries) != expected:
                raise SystemExit(
                    f"{archive.name}: expected {expected} slide images, found {len(entries)}"
                )
            if len(entries) % 7:
                raise SystemExit(f"{archive.name}: image count is not divisible into 7-slide carousels")

            for offset in range(0, len(entries), 7):
                carousel_number += 1
                carousel_id = f"carousel-{carousel_number:03d}"
                output_dir = PUBLISHED / carousel_id
                output_dir.mkdir(parents=True)
                image_urls = []
                for slide_index, member in enumerate(entries[offset:offset + 7], start=1):
                    data = zf.read(member)
                    suffix = Path(member).suffix.lower()
                    if not image_signature(data, suffix):
                        raise SystemExit(f"Invalid {suffix} image data in {archive.name}: {member}")
                    filename = f"slide-{slide_index:02d}{suffix}"
                    output = output_dir / filename
                    output.write_bytes(data)
                    relative = output.relative_to(ROOT).as_posix()
                    image_urls.append(
                        f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/{relative}"
                    )
                    total_images += 1
                carousels.append({
                    "id": carousel_id,
                    "batch": batch_number,
                    "images": image_urls,
                    "caption": (
                        "Practical advice for building your career in the Gulf. "
                        "Swipe through, save the guidance and explore Gulf opportunities "
                        "at https://www.jobsultan.com. "
                        "#JobSultan #GulfJobs #JobsInSaudi #JobsInUAE "
                        "#JobsInQatar #GulfCareers #CareerAdvice"
                    ),
                })

    if carousel_number != 60 or total_images != 420:
        raise SystemExit(
            f"Expected 60 carousels / 420 slides; extracted {carousel_number} / {total_images}"
        )

    manifest = {
        "version": 1,
        "carousel_count": carousel_number,
        "slide_count": total_images,
        "slides_per_carousel": 7,
        "asset_repository": f"https://github.com/{OWNER}/{REPO}",
        "carousels": carousels,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"Extracted {carousel_number} carousels and {total_images} slide images.")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
