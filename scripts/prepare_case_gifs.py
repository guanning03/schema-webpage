"""Render paired, complete ARC levels from recorded observations.

Every action is retained, including failed attempts and resets. Both sides
advance at the same action pace, with shared pauses at the paper's key events.
Only annotation outlines and status text are added to the native pixel grids.
Render at 3x density for crisp text on Retina displays. A fixed palette retains
the game colors and the antialiased text's actual foreground/background ramp.
"""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent
OUT = SITE / "assets/cases"
OUT.mkdir(exist_ok=True)
EVIDENCE = json.loads((ROOT / "paper/figures/case_evidence.json").read_text())
PALETTE = ["#FFFFFF", "#CCCCCC", "#999999", "#666666", "#333333", "#000000",
           "#E53AA3", "#FF7BCC", "#F93C31", "#1E93FF", "#88D8F1", "#FFDC00",
           "#FF851B", "#921231", "#4FCC30", "#A356D6"]
LUT = np.array([[int(c[i:i+2], 16) for i in (1, 3, 5)] for c in PALETTE], dtype=np.uint8)
DENSITY = 3
SIZE, GAP, FOOT = [value * DENSITY for value in (384, 24, 42)]
FONT = ImageFont.truetype(str(SITE / "static/fonts/google-sans.ttf"), 18 * DENSITY)
INDEXED_PALETTE = Image.new("P", (1, 1))
text_color = np.array([75, 85, 99])
text_ramp = np.rint(np.linspace(text_color, [255, 255, 255], 224)).astype(np.uint8)
palette = LUT.flatten().tolist() + text_ramp.flatten().tolist() + [17, 24, 39]
INDEXED_PALETTE.putpalette(palette + [0] * (768 - len(palette)))


def archive_events(name, work):
    archive = ROOT / "results/arc3-ablation-runs" / f"{name}.tar.zst"
    cached = Path("/tmp/schema-full-level-cases") / f"{name}.jsonl"
    if cached.is_file():
        return cached, str(archive.relative_to(ROOT))
    names = subprocess.check_output(["tar", "-tf", str(archive)], text=True).splitlines()
    members = [p for p in names if p.endswith("/events.jsonl") and "/.rt/" not in p]
    assert len(members) == 1, members
    target = work / f"{name}.jsonl"
    with target.open("wb") as stream:
        subprocess.run(["tar", "-xOf", str(archive), members[0]], stdout=stream, check=True)
    return target, str(archive.relative_to(ROOT))


def level_frames(path, target, source):
    frames, steps, seqs = [], [], []
    previous, level, completed = None, 0, False
    for line in path.open():
        e = json.loads(line)
        if e["kind"] == "turn_started" and previous is None:
            previous, level = e["grid"], e["level"]
        if e["kind"] != "action_taken":
            continue
        if level == target:
            if not frames:
                frames.append(np.asarray(previous, dtype=np.uint8))
            steps.append(e["step_index"])
            seqs.append(e["seq"])
            frame = np.asarray(e["grid"], dtype=np.uint8)
            if e.get("level_up"):
                # The post-action grid belongs to the next level. Recover the
                # recorded completion animation, retaining the prior state if
                # the source has no animation ticks.
                frame = np.array(previous, dtype=np.uint8)
                for tick in e.get("ticks") or []:
                    if "g" in tick:
                        frame = np.asarray(tick["g"], dtype=np.uint8)
                    else:
                        for x, y, color in tick.get("d", []):
                            frame[y, x] = color
                frames.append(frame)
                completed = True
                break
            frames.append(frame)
        previous, level = e["grid"], e["level"]
    assert completed, f"Incomplete level: {source} / {target + 1}"
    assert len(frames) == len(steps) + 1
    assert steps == list(range(steps[0], steps[-1] + 1)), "Missing action"
    assert all(f.shape == (64, 64) and f.max() < 16 for f in frames)
    return frames, dict(source=source, level=target + 1, actions=len(steps),
                        action_indices=steps, event_sequences=seqs,
                        grids_sha256=hashlib.sha256(np.stack(frames).tobytes()).hexdigest())


def color_box(grid, colors):
    yy, xx = np.where(np.isin(grid, colors))
    return [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]


def pair(left, right, statuses, outlines):
    # Work directly in indexed color: RGB quantization can map pure white to
    # a nearby antialias shade. Native board indices must remain exact.
    image = Image.new("P", (SIZE * 2 + GAP, SIZE + FOOT), 0)
    image.putpalette(INDEXED_PALETTE.getpalette())
    draw = ImageDraw.Draw(image)
    text_mask = Image.new("L", (SIZE * 2 + GAP, FOOT), 0)
    text_draw = ImageDraw.Draw(text_mask)
    for side, grid in enumerate([left, right]):
        x = side * (SIZE + GAP)
        board = Image.fromarray(grid)
        board.putpalette(INDEXED_PALETTE.getpalette())
        image.paste(board.resize((SIZE, SIZE), Image.Resampling.NEAREST), (x, 0))
        for box in outlines[side]:
            x0, y0, x1, y1 = box
            scale = SIZE / 64
            padding = 3 * DENSITY
            rect = (x + x0 * scale - padding, y0 * scale - padding,
                    x + x1 * scale + padding, y1 * scale + padding)
            draw.rounded_rectangle(rect, radius=5 * DENSITY, outline=240, width=5 * DENSITY)
            draw.rounded_rectangle(rect, radius=5 * DENSITY, outline=0, width=2 * DENSITY)
        text_draw.text((x + SIZE / 2, 12 * DENSITY), statuses[side], font=FONT,
                       fill=255, anchor="mt")
    alpha = np.asarray(text_mask, dtype=np.uint16)
    indices = (16 + np.rint((255 - alpha) * 223 / 255)).astype(np.uint8)
    indices[alpha == 0] = 0
    text_layer = Image.fromarray(indices)
    text_layer.putpalette(INDEXED_PALETTE.getpalette())
    image.paste(text_layer, (0, SIZE))
    return image


def replay(name, left, right, metadata, pace, highlights):
    # Spool frames to disk to avoid retaining 1,220 full-resolution images.
    with tempfile.TemporaryDirectory(prefix=f"schema-{name}-3x-") as temporary:
        return render_replay(name, left, right, metadata, pace, highlights, Path(temporary))


def indexed_frames(paths):
    for path in paths:
        with Image.open(path) as frame:
            yield frame.copy()


def render_replay(name, left, right, metadata, pace, highlights, work):
    counts = [len(left) - 1, len(right) - 1]
    frames, durations = [], []
    for step in range(max(counts) + 1):
        labels = [f"Completed · {n:,} actions" if step >= n else f"{step:,} actions"
                  for n in counts]
        event = highlights.get(step, {})
        for side, label in event.get("labels", {}).items():
            labels[side] = label
        image = pair(left[min(step, counts[0])], right[min(step, counts[1])],
                     labels, event.get("outlines", [[], []]))
        if step in highlights:
            image.save(OUT / f"{name}_key_{step}_3x.png")
        if step == min(highlights):
            image.save(OUT / f"{name}_full_3x.png")
        path = work / f"{step:04d}.png"
        image.save(path, compress_level=1)
        frames.append(path)
        durations.append(event.get("hold_ms", pace))
    durations[0], durations[-1] = 900, 1800
    with Image.open(frames[0]) as first:
        first.save(OUT / f"{name}_full_3x.gif", save_all=True,
                   append_images=indexed_frames(frames[1:]),
                   duration=durations, loop=0, disposal=1, optimize=True)
    record = dict(left=metadata[0], right=metadata[1], timeline_steps=len(frames),
                  action_pace_ms=pace, duration_ms=sum(durations), highlights=highlights,
                  pixel_density=DENSITY, width=SIZE * 2 + GAP, height=SIZE + FOOT)
    print(f"Ready: {name} · {counts[0]} / {counts[1]} actions · {len(frames)} frames", flush=True)
    return record


def main():
    manifest = {}
    with tempfile.TemporaryDirectory(prefix="schema-cases-") as temporary:
        work = Path(temporary)
        def ablation(name, level):
            path, source = archive_events(name, work)
            return level_frames(path, level - 1, source)
        def schema(game, level):
            path = ROOT / f"results/arc3-runs/opus48/{game}/events.jsonl"
            return level_frames(path, level - 1, str(path.relative_to(ROOT)))

        left, lm = ablation("cn04_ctrl2", 5)
        right, rm = ablation("cn04_text", 5)
        assert (lm["actions"], rm["actions"]) == (279, 1219)
        assert np.array_equal(left[-1], EVIDENCE["representation"]["recorded_frames"][-1]["grid"])
        manifest["representation"] = replay("representation", left, right, [lm, rm], 30, {
            235: dict(hold_ms=1200, outlines=[[color_box(left[235], [8, 11, 12])], []],
                      labels={0: "Before growth"}),
            239: dict(hold_ms=1400, outlines=[[color_box(left[239], [8, 11, 12])], []],
                      labels={0: "After four growth actions"}),
            279: dict(hold_ms=1200),
        })

        left, lm = schema("ar25", 3)
        right, rm = ablation("ar25_nobt", 3)
        assert (lm["actions"], rm["actions"]) == (41, 41)
        # The model revision at turn 16 happens after 17 actions in level 3.
        # White pixels identify the selected piece, which this revision concerns.
        selected = color_box(right[17], [0])
        assert selected == [46, 28, 56, 32], selected
        manifest["certification"] = replay("certification", left, right, [lm, rm], 160, {
            17: dict(hold_ms=1800, outlines=[[], [[44, 26, 57, 34]]],
                     labels={1: "Active-piece model revised"}),
        })

        left, lm = schema("ls20", 5)
        right, rm = ablation("ls20_nobfs", 5)
        assert (lm["actions"], rm["actions"]) == (65, 233)
        assert np.array_equal(left[54][55:61:2, 3:9:2], left[54][6:9, 55:58])
        symbols = [[3, 55, 9, 61], [55, 6, 58, 9]]
        manifest["planning"] = replay("planning", left, right, [lm, rm], 70, {
            52: dict(hold_ms=1000, outlines=[symbols, []], labels={0: "Final 13-action plan begins"}),
            54: dict(hold_ms=1600, outlines=[symbols, []], labels={0: "Carried symbol matches target"}),
            65: dict(hold_ms=1000),
        })

        left, lm = schema("ls20", 2)
        right, rm = ablation("ls20_nompc", 2)
        assert (lm["actions"], rm["actions"]) == (59, 143)
        assert np.array_equal(right[55], EVIDENCE["verification"]["actual"])
        assert np.array_equal(right[92], EVIDENCE["verification"]["revisit"])
        station = [15, 16, 18, 19]
        manifest["verification"] = replay("verification", left, right, [lm, rm], 90, {
            54: dict(hold_ms=1000, outlines=[[], [station]], labels={1: "Refueled at this station"}),
            55: dict(hold_ms=1600, outlines=[[], [station]], labels={1: "Station consumed · first mismatch"}),
            92: dict(hold_ms=1400, outlines=[[], [station]], labels={1: "Returns to the spent station"}),
            93: dict(hold_ms=1200, outlines=[[], [[12, 61, 55, 63]]], labels={1: "Energy depleted"}),
        })
    (OUT / "full_level_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
