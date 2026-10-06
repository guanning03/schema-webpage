"""Export the 21 DiG-bench website replays with model-name-only subtitles."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import tempfile

SITE = Path(__file__).resolve().parents[1]
SOURCE = SITE.parent / "supp_videos_720p/gameplay_videos"


def prepare(source):
    stem = source.stem.replace("schema_max_", "schema_")
    output = SITE / "assets/videos" / f"{stem}.mp4"
    poster = SITE / "assets/posters" / f"{stem}.jpg"
    with tempfile.TemporaryDirectory(prefix="schema-dig-") as work:
        staged = Path(work) / "replay.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
            "-vf", "drawbox=x=1044:y=106:w=200:h=30:color=0x0e1116:t=fill",
            "-c:v", "libx264", "-threads", "2", "-preset", "fast", "-crf", "20",
            "-an", "-movflags", "+faststart", str(staged),
        ], check=True)
        staged.replace(output)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "4",
        "-i", str(output), "-frames:v", "1", "-q:v", "2", str(poster),
    ], check=True)
    return stem


if __name__ == "__main__":
    sources = sorted(SOURCE.glob("digbench_schema_max_*.mp4"))
    assert len(sources) == 21
    with ThreadPoolExecutor(max_workers=3) as pool:
        for stem in pool.map(prepare, sources):
            print(f"Ready: {stem}", flush=True)
