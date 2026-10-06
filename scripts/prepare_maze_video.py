"""Build the website replay from the original MazeBench video.

Requires ffmpeg and the Pillow/matplotlib dependencies of the original renderer.
The source replay and its renderer remain unchanged. Only the requested HUD
fields and the intro/outro action totals are removed from the website edition.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
SOURCE_DIR = SITE.parent / "gameplay_videos"
sys.path.insert(0, str(SOURCE_DIR / "_src"))
from vidcommon import Image, SALMON, SAGE, banner

SOURCE = SOURCE_DIR / "mazebench_schema_high_full_run.mp4"
OUTPUT = SITE / "assets/videos/mazebench_schema_full_run.mp4"
POSTER = SITE / "assets/posters/mazebench_schema_full_run.jpg"


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


with tempfile.TemporaryDirectory(prefix="schema-maze-") as work:
    work = Path(work)
    # These are the original, unoverlaid stills used for the opening and closing
    # cards. Preserve their game states and all other HUD information.
    cards = [
        ("intro", "2.5", "MAZEBENCH", "one continuous run", SALMON),
        ("outro", "466.65", "33 GEMS · 139 ROOMS", "", SAGE),
    ]
    for name, timestamp, title, subtitle, accent in cards:
        path = work / f"{name}.png"
        ffmpeg("-ss", timestamp, "-i", SOURCE, "-frames:v", "1", path)
        with Image.open(path) as frame:
            frame = frame.convert("RGB")
            banner(frame, (560, 540), title, subtitle, accent, 760)
            frame.save(path)

    # Coordinates follow the 1920 × 1080 source renderer. The three uniform
    # background regions contain only (high), the action counter, and the
    # current action label/value. The room map and gem curve stay untouched.
    graph = (
        "[0:v]fps=30[video];"
        "[video][1:v]overlay=enable='lt(t,2.5)'[intro];"
        "[intro][2:v]overlay=enable='gte(t,466.66)'[cards];"
        "[cards]drawbox=x=1550:y=160:w=330:h=44:color=0x0e1116:t=fill,"
        "drawbox=x=1556:y=224:w=340:h=100:color=0x0e1116:t=fill,"
        "drawbox=x=1584:y=596:w=336:h=94:color=0x0e1116:t=fill,"
        "scale=1280:720:flags=lanczos,format=yuv420p[out]"
    )
    staged = work / "replay.mp4"
    print("Exporting MazeBench website replay…", flush=True)
    ffmpeg("-i", SOURCE, "-i", work / "intro.png", "-i", work / "outro.png",
           "-filter_complex", graph, "-map", "[out]", "-an",
           "-c:v", "libx264", "-preset", "fast", "-crf", "19",
           "-movflags", "+faststart", staged)
    staged.replace(OUTPUT)
    ffmpeg("-ss", "12", "-i", OUTPUT, "-frames:v", "1", "-q:v", "2", POSTER)
    print(f"Wrote {OUTPUT}\nWrote {POSTER}", flush=True)
