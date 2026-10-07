"""Reveal Figure 1 in reading order, close its loop, then show the results."""
from pathlib import Path
import json
import subprocess

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WORK = ROOT.parent.parent / "schema-twitter/.build/overview"
WORK.mkdir(parents=True, exist_ok=True)
source = Image.open(ASSETS / "02-paper-figure1.png").convert("RGB")
width, height = source.size
pixels = np.asarray(source).astype(np.float32)
reveal = np.full((height, width), 4.5, dtype=np.float32)
fade = np.full((height, width), .65, dtype=np.float32)
stages = []


def bounds(coords):
    return tuple(round(v * scale) for v, scale in zip(
        coords, [width / 2048, height / 1056, width / 2048, height / 1056]
    ))


def panel(name, coords, start, duration=.5):
    x0, y0, x1, y1 = bounds(coords)
    reveal[y0:y1, x0:x1] = start
    fade[y0:y1, x0:x1] = duration
    stages.append(dict(element=name, start=start, end=start + duration, transition="fade"))


def arrow(name, coords, start, direction, duration=.3):
    x0, y0, x1, y1 = bounds(coords)
    # Isolate the original gray arrow, including its antialiased edge. Panel
    # borders and nearby lettering retain their own reveal times.
    crop = pixels[y0:y1, x0:x1]
    ink = np.array([117., 106., 92.], dtype=np.float32)  # white minus arrow RGB
    delta = 255 - crop
    opacity = np.sum(delta * ink, axis=2) / np.sum(ink * ink)
    residual = np.max(np.abs(delta - opacity[:, :, None] * ink), axis=2)
    mask = (opacity > .006) & (opacity < 1.03) & (residual < 3)
    ramp = np.linspace(0, duration, x1 - x0, dtype=np.float32)
    if direction == "left":
        ramp = ramp[::-1]
    times = np.broadcast_to(start + ramp, mask.shape)
    reveal[y0:y1, x0:x1][mask] = times[mask]
    fade[y0:y1, x0:x1][mask] = .15
    stages.append(dict(element=name, start=start, end=start + duration + .15,
                       transition="follow arrow " + direction))


panel("left: observe", (0, 0, 620, 570), 0)
panel("middle: induce a program", (620, 0, 1412, 570), 1.05)
panel("right: plan and act", (1412, 0, 2048, 570), 2.1)
arrow("observe to program", (558, 72, 690, 142), .7, "right")
arrow("program to planning", (1360, 72, 1486, 142), 1.75, "right")
arrow("return loop: leaving the right panel", (1364, 498, 1504, 575), 3.05, "left", .35)
panel("interact, learn, and improve", (740, 570, 1320, 614), 3.4, .4)
arrow("return loop: back to observation", (556, 482, 702, 575), 3.6, "left", .35)
panel("all three benchmark results", (0, 615, 2048, 1056), 4.5, .65)

fps = 30
duration = 8.5
snapshots = {round(t * fps): t for t in [.6, 1.65, 2.7, 3.5, 4.15, 4.8, 5.3, 8.4]}
command = [
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
    "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast",
    "-crf", "15", "-pix_fmt", "yuv420p", "-threads", "2", "-movflags", "+faststart",
    str(ASSETS / "02-overview-animation.mp4"),
]
delta = 255 - pixels
with subprocess.Popen(command, stdin=subprocess.PIPE) as process:
    for i in range(round(duration * fps)):
        t = i / fps
        alpha = np.clip((t - reveal) / fade, 0, 1)
        alpha = alpha * alpha * (3 - 2 * alpha)
        frame = np.clip(np.rint(255 - delta * alpha[:, :, None]), 0, 255).astype(np.uint8)
        process.stdin.write(frame.tobytes())
        if i in snapshots:
            Image.fromarray(frame).save(WORK / f"at-{snapshots[i]:04.2f}.png")
    process.stdin.close()
    process.wait()
    assert process.returncode == 0
assert np.array_equal(frame, np.asarray(source)), "Final frame must reproduce the source figure."
timeline = dict(
    version=1, source="paper_arxiv/figures/teaser.pdf", duration_seconds=duration,
    stages=stages, final_hold_seconds=3.35,
    notes="Original panels appear left to right, then the return arrows lead back to observation. All three result panels fade in together. The final figure is unchanged."
)
(ASSETS / "02-overview-animation-timeline.json").write_text(json.dumps(timeline, indent=2) + "\n")
print(f"Exported Figure 1: {duration}s, {width}x{height}, complete original figure held at the end.")
