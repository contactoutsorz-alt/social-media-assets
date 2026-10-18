"""Convert user-uploaded clips into silent, portrait-safe Instagram Reels.

Only processes existing videos. Never adds generated footage or replaces originals.
Requires ffmpeg and ffprobe (installed by the GitHub workflow).
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "jobsultan/instagram-reels/uploads"
READY = ROOT / "jobsultan/instagram-reels/silent"
MANIFEST = READY / "manifest.json"
VALID = {".mp4", ".mov", ".m4v", ".webm"}
MAX_DURATION = 180.0
MAX_OUTPUT_BYTES = 90_000_000


def command(*parts):
    return subprocess.run(parts, check=True, capture_output=True, text=True).stdout.strip()


def probe(path):
    return json.loads(command(
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height,codec_name",
        "-of", "json", str(path)
    ))


def transform(source, target):
    tmp = target.with_suffix(".temporary.mp4")
    try:
        subprocess.run([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(source), "-map", "0:v:0", "-an",
            "-vf", "fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,"
                   "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "25",
            "-maxrate", "2500k", "-bufsize", "5000k",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(tmp)
        ], check=True)
        checked = probe(tmp)
        streams = checked.get("streams", [])
        video = [s for s in streams if s.get("codec_type") == "video"]
        audio = [s for s in streams if s.get("codec_type") == "audio"]
        if len(video) != 1 or audio or video[0].get("codec_name") != "h264":
            raise ValueError(f"{source.name}: output must contain H264 video and NO audio")
        if (video[0].get("width"), video[0].get("height")) != (1080, 1920):
            raise ValueError(f"{source.name}: expected portrait 1080x1920 output")
        if tmp.stat().st_size > MAX_OUTPUT_BYTES:
            raise ValueError(f"{source.name}: silent MP4 exceeds 90 MB; shorten the source clip")
        tmp.replace(target)
    finally:
        tmp.unlink(missing_ok=True)


def main():
    SOURCE.mkdir(parents=True, exist_ok=True)
    READY.mkdir(parents=True, exist_ok=True)
    videos = [f for f in SOURCE.iterdir() if f.is_file() and f.suffix.lower() in VALID]
    prepared = []
    for source in sorted(videos, key=lambda x: x.name.lower()):
        checked = probe(source)
        streams = checked.get("streams", [])
        if not any(s.get("codec_type") == "video" for s in streams):
            raise ValueError(f"{source.name}: no video stream found")
        duration = float(checked.get("format", {}).get("duration", "0"))
        if not 3 <= duration <= MAX_DURATION:
            raise ValueError(f"{source.name}: Reels must be between 3 and 180 seconds here")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        stem = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-")[:55] or "video"
        output = READY / f"{stem}-{digest}-silent.mp4"
        if not output.exists():
            transform(source, output)
            print(f"Prepared silent Reel: {source.name} -> {output.name}")
        else:
            meta = probe(output)
            if any(s.get("codec_type") == "audio" for s in meta.get("streams", [])):
                raise ValueError(f"Existing processed Reel has audio: {output.name}")
        if output.stat().st_size > MAX_OUTPUT_BYTES:
            raise ValueError(f"Ready Reel exceeds 90 MB: {output.name}")
        prepared.append({"source": source.name, "filename": output.name,
                         "duration_seconds": round(duration, 1),
                         "bytes": output.stat().st_size, "audio_removed": True})
    MANIFEST.write_text(json.dumps({"videos": prepared}, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(prepared)} silent Instagram Reels; manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
