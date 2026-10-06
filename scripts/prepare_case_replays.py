"""Create seekable, silent case replays without dropping any recorded frame.

GIF remains the rendering source. MP4 gives the page real pause/resume support
and keeps the playback position when a case scrolls out of view. Explicit time
base and disabled B-frames preserve every GIF frame's timestamp and duration.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

from PIL import Image

SITE = Path(__file__).resolve().parents[1]
OUT = SITE / "assets/cases"


def convert(item):
    name, record = item
    source = OUT / f"{name}_full_3x.gif"
    video = OUT / f"{name}_full_3x.mp4"
    poster = OUT / f"{name}_start_3x.png"
    with Image.open(source) as image:
        assert image.n_frames == record["timeline_steps"]
        image.seek(0)
        image.save(poster)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-an", "-fps_mode", "passthrough", "-enc_time_base", "1/1000",
        "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-bf", "0",
        "-pix_fmt", "yuv420p", "-threads", "2", "-movflags", "+faststart",
        "-video_track_timescale", "1000", str(video),
    ], check=True)
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=pts_time,duration_time",
        "-show_entries", "stream=width,height,nb_frames,duration", "-of", "json", str(video),
    ]))
    frames, stream = probe["frames"], probe["streams"][0]
    assert len(frames) == record["timeline_steps"]
    assert (stream["width"], stream["height"]) == (record["width"], record["height"])
    elapsed = 0
    for index, frame in enumerate(frames):
        duration = record["highlights"].get(str(index), {}).get("hold_ms", record["action_pace_ms"])
        if index == 0:
            duration = 900
        if index == len(frames) - 1:
            duration = 1800
        assert round(float(frame["pts_time"]) * 1000) == elapsed, (name, index, "timestamp")
        assert round(float(frame["duration_time"]) * 1000) == duration, (name, index, "duration")
        elapsed += duration
    assert elapsed == record["duration_ms"]
    assert round(float(stream["duration"]) * 1000) == elapsed
    record["web_replay"] = {"video": video.name, "poster": poster.name, "frames": len(frames), "duration_ms": elapsed}
    print(f"Verified {name}: all {len(frames)} frames and {elapsed} ms retained.", flush=True)
    return name, record


def main():
    manifest = json.loads((OUT / "full_level_manifest.json").read_text())
    with ThreadPoolExecutor(max_workers=2) as pool:
        converted = dict(pool.map(convert, manifest.items()))
    (OUT / "full_level_manifest.json").write_text(json.dumps(converted, indent=2) + "\n")


if __name__ == "__main__":
    main()
