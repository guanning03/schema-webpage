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
FONT = ImageFont.truetype(str(SITE / "static/fonts/castoro.ttf"), 16 * DENSITY)
INDEXED_PALETTE = Image.new("P", (1, 1))
text_color = np.array([75, 85, 99])
text_ramp = np.rint(np.linspace(text_color, [255, 255, 255], 224)).astype(np.uint8)
ANNOTATION_RED = [178, 31, 75]  # #B21F4B; distinct from native red #F93C31.
palette = LUT.flatten().tolist() + text_ramp.flatten().tolist() + [17, 24, 39] + ANNOTATION_RED
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
            padding = 2 * DENSITY
            rect = (x + x0 * scale - padding, y0 * scale - padding,
                    x + x1 * scale + padding, y1 * scale + padding)
            # A thin white halo separates the editorial red from every board
            # color; the box is positioned in the source grid's coordinates.
            draw.rectangle(rect, outline=0, width=4 * DENSITY)
            inset = DENSITY
            draw.rectangle((rect[0]+inset, rect[1]+inset, rect[2]-inset, rect[3]-inset),
                           outline=241, width=2 * DENSITY)
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
    durations[0], durations[-1] = 2200, 3500
    with Image.open(frames[0]) as first:
        first.save(OUT / f"{name}_full_3x.gif", save_all=True,
                   append_images=indexed_frames(frames[1:]),
                   duration=durations, loop=0, disposal=1, optimize=True)
    record = dict(left=metadata[0], right=metadata[1], timeline_steps=len(frames),
                  action_pace_ms=pace, duration_ms=sum(durations), highlights=highlights,
                  frame_durations_ms=durations,
                  pixel_density=DENSITY, width=SIZE * 2 + GAP, height=SIZE + FOOT)
    print(f"Ready: {name} · {counts[0]} / {counts[1]} actions · {len(frames)} frames", flush=True)
    return record


def crop_asset(name, grid, box):
    """Enlarged native pixels for the page's small explanatory insets."""
    x0, y0, x1, y1 = box
    native = np.asarray(grid, dtype=np.uint8)[y0:y1, x0:x1]
    filename = f"{name}.png"
    image = Image.fromarray(LUT[native])
    image.resize((native.shape[1] * 12, native.shape[0] * 12), Image.Resampling.NEAREST).save(OUT / filename)
    return filename


def detail_image(label, filename):
    return dict(label=label, image=filename)


def join_chapters(name, chapters):
    paths = [OUT / f"{chapter}_full_3x.gif" for chapter, _ in chapters]
    durations = [d for _, record in chapters for d in record["frame_durations_ms"]]
    def frames():
        for path in paths:
            with Image.open(path) as source:
                for i in range(source.n_frames):
                    source.seek(i)
                    yield source.copy()
    source = frames()
    first = next(source)
    first.save(OUT / f"{name}_full_3x.gif", save_all=True, append_images=source,
               duration=durations, loop=0, disposal=1, optimize=True)
    first.save(OUT / f"{name}_full_3x.png")
    record = dict(chapters=[r for _, r in chapters], timeline_steps=len(durations),
                  duration_ms=sum(durations), frame_durations_ms=durations,
                  width=SIZE*2+GAP, height=SIZE+FOOT, pixel_density=DENSITY,
                  highlights={}, segments=[])
    offset = 0
    for _, chapter in chapters:
        record["segments"].append(dict(start=offset, level=chapter["left"]["level"],
                                       counts=[chapter["left"]["actions"], chapter["right"]["actions"]]))
        offset += chapter["timeline_steps"]
    for side in ["left", "right"]:
        record[side] = dict(actions=sum(c[side]["actions"] for _, c in chapters),
                            levels=[c[side] for _, c in chapters])
    return record


def certification_later_evidence(path):
    events = [json.loads(line) for line in path.open()]
    actions = {e["step_index"]: e for e in events if e["kind"] == "action_taken"}
    mismatch = next(e for e in events if e["kind"] == "model_mispredicted" and e["step_index"] == 193)
    assert np.array_equal(mismatch["actual"], actions[193]["grid"])
    assert not np.array_equal(mismatch["predicted"], mismatch["actual"])
    assert actions[194]["action"] == 0  # The next action is a reset.
    # No model correction is made between the mismatch and the next plan.
    start = next(e["seq"] for e in events if e["kind"] == "turn_started" and e["turn"] == 36)
    end = next(e["seq"] for e in events if e["kind"] == "turn_committed" and e["turn"] == 36)
    edits = [e for e in events if start < e["seq"] < end and e["kind"] == "tool_started"
             and e.get("name") in ["write_file", "edit_file"]
             and e.get("args", {}).get("path") == "world_model_v5.py"]
    assert not edits, "The unchanged-model claim no longer matches the trace."
    reason = next(e["reason"] for e in events if e["seq"] == end)
    record = dict(source="results/arc3-ablation-runs/ar25_nobt.tar.zst", level=6,
                  local_action=53, history_index=193, mismatch_seq=mismatch["seq"],
                  next_plan_seq=end, model_edits_before_next_plan=len(edits),
                  next_plan_reason=reason, before=actions[192]["grid"],
                  predicted=mismatch["predicted"], observed=mismatch["actual"])
    (OUT / "certification_later_evidence.json").write_text(json.dumps(record, indent=2)+"\n")
    return record


def main():
    manifest = {}
    scenes = {}
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
        before_box = color_box(left[235], [8, 11, 12])
        after_box = color_box(left[239], [8, 11, 12])
        before = crop_asset("growth_before", left[235], before_box)
        after = crop_asset("growth_after", left[239], after_box)
        manifest["representation"] = replay("representation", left, right, [lm, rm], 50, {
            235: dict(hold_ms=2400, outlines=[[before_box], []]),
            236: dict(hold_ms=400, outlines=[[color_box(left[236], [8, 11, 12])], []]),
            237: dict(hold_ms=400, outlines=[[color_box(left[237], [8, 11, 12])], []]),
            238: dict(hold_ms=400, outlines=[[color_box(left[238], [8, 11, 12])], []]),
            239: dict(hold_ms=3200, outlines=[[after_box], []]),
            279: dict(hold_ms=2600),
        })
        scenes["representation"] = [
            dict(step=0, text="Join every connector without overlapping the pieces. One piece changes shape as it grows."),
            dict(step=235, text="Schema models the growing piece explicitly. Watch its connectors change."),
            dict(step=239, text="Four growth actions create seven connectors. The program searches for a non-overlapping arrangement.",
                 detail=[detail_image("Before growth", before), detail_image("After growth", after)]),
            dict(step=250, text="The pieces now move into the computed arrangement."),
            dict(step=279, text="Schema finishes in 279 actions. The prose model is still working through the same level."),
            dict(step=1219, text="Both runs are complete: 279 actions with Schema, 1,219 with the prose model."),
        ]

        left, lm = schema("ar25", 3)
        right, rm = ablation("ar25_nobt", 3)
        assert (lm["actions"], rm["actions"]) == (41, 41)
        selected = color_box(right[17], [0])
        assert selected == [46, 28, 56, 32], selected
        chapter3 = replay("certification_level3", left, right, [lm, rm], 200, {
            17: dict(hold_ms=6000, outlines=[[], [[44, 26, 57, 34]]]),
        })
        scenes["certification"] = [
            dict(step=0, text="Move pieces and mirror axes until the reflected shapes cover the targets."),
            dict(step=17, text="Without certification, fixing the selected-piece rule breaks predictions for a past level.",
                 detail=[dict(label="Past level · before revision", value="16 / 16"),
                         dict(label="Same transitions · after", value="1 / 16")]),
            dict(step=41, text="Both finish in 41 actions. The difference is retained knowledge: the revised model has broken 15 of 16 old predictions.",
                 detail=[dict(label="Past level · before revision", value="16 / 16"),
                         dict(label="Same transitions · after", value="1 / 16")]),
        ]

        left, lm = schema("ar25", 6)
        right, rm = ablation("ar25_nobt", 6)
        assert (lm["actions"], rm["actions"]) == (53, 119)
        evidence_path, _ = archive_events("ar25_nobt", work)
        later = certification_later_evidence(evidence_path)
        assert np.array_equal(right[53], later["observed"])
        predicted_crop = crop_asset("certification_later_predicted", later["predicted"], [40, 7, 60, 32])
        actual_crop = crop_asset("certification_later_observed", later["observed"], [40, 7, 60, 32])
        chapter6 = replay("certification_level6", left, right, [lm, rm], 150, {
            52: dict(hold_ms=2000, outlines=[[], [[42, 9, 57, 30]]]),
            53: dict(hold_ms=5000, outlines=[[], [[42, 24, 54, 30]]]),
            54: dict(hold_ms=2800),
        })
        manifest["certification"] = join_chapters("certification", [
            ("certification_level3", chapter3), ("certification_level6", chapter6)])
        offset = chapter3["timeline_steps"]
        scenes["certification"] += [
            dict(step=offset, text="Later, on level 6, the agent must keep track of multiple separate pieces."),
            dict(step=offset+52, text="On the right, two pieces touch diagonally. The model incorrectly merges their identities."),
            dict(step=offset+53, text="Schema is complete. The other model predicts no movement, but the selected piece moves left.",
                 detail=[detail_image("Predicted · no move", predicted_crop), detail_image("Observed · moves left", actual_crop)]),
            dict(step=offset+54, text="Without certifying the model against that observed failure, the agent resets and takes a detour."),
            dict(step=offset+119, text="The later level takes 119 actions without certification, compared with 53 for Schema."),
        ]

        left, lm = schema("ls20", 5)
        right, rm = ablation("ls20_nobfs", 5)
        assert (lm["actions"], rm["actions"]) == (65, 233)
        assert np.array_equal(left[54][55:61:2, 3:9:2], left[54][6:9, 55:58])
        symbols = [[3, 55, 9, 61], [55, 6, 58, 9]]
        target = crop_asset("planning_target", left[54], [55, 6, 58, 9])
        symbol_images = [crop_asset(f"planning_symbol_{i}", left[i], [3, 55, 9, 61]) for i in [52, 53, 54]]
        manifest["planning"] = replay("planning", left, right, [lm, rm], 90, {
            52: dict(hold_ms=2200, outlines=[[[15, 34, 25, 45]], []]),
            53: dict(hold_ms=1800, outlines=[[[15, 34, 25, 45]], []]),
            54: dict(hold_ms=3200, outlines=[[[15, 34, 25, 45]], []]),
            65: dict(hold_ms=2400),
        })
        scenes["planning"] = [
            dict(step=0, text="Match the carried symbol to the goal. Contact with the moving white marker rotates it."),
            dict(step=52, text="Schema plans the last 13 actions. First, time contact with the moving marker.",
                 detail=[detail_image("Carried symbol", symbol_images[0]), detail_image("Target", target)]),
            dict(step=53, text="Down: the player approaches the moving rotation marker.",
                 detail=[detail_image("After down", symbol_images[1]), detail_image("Target", target)]),
            dict(step=54, text="Up: contact rotates the symbol into the target shape. Eleven planned actions remain.",
                 detail=[detail_image("After up", symbol_images[2]), detail_image("Target", target)]),
            dict(step=55, text="The symbol matches. Schema follows the remaining route to the goal."),
            dict(step=65, text="Schema finishes in 65 actions. Without planning, the agent continues working out its route and transformations."),
            dict(step=233, text="Both runs are complete: 65 actions with Schema, 233 without planning."),
        ]

        left, lm = schema("ls20", 2)
        right, rm = ablation("ls20_nompc", 2)
        assert (lm["actions"], rm["actions"]) == (59, 143)
        assert np.array_equal(right[55], EVIDENCE["verification"]["actual"])
        assert np.array_equal(right[92], EVIDENCE["verification"]["revisit"])
        schema_path = ROOT / "results/arc3-runs/opus48/ls20/events.jsonl"
        mismatches = [e for line in schema_path.open() if (e := json.loads(line))["kind"] == "model_mispredicted" and e["step_index"] == 31]
        assert len(mismatches) == 1 and "dropped" in mismatches[0]["surprise"]
        predicted = np.asarray(mismatches[0]["predicted"], dtype=np.uint8)
        yy, xx = np.where(predicted != left[13])
        assert [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)] == [15, 16, 18, 19]
        crop = [12, 13, 23, 24]
        sp = crop_asset("schema_station_predicted", predicted, crop)
        sa = crop_asset("schema_station_observed", left[13], crop)
        rp = crop_asset("ablation_station_predicted", EVIDENCE["verification"]["prediction"], crop)
        ra = crop_asset("ablation_station_observed", right[55], crop)
        station = [15, 16, 18, 19]
        manifest["verification"] = replay("verification", left, right, [lm, rm], 120, {
            12: dict(hold_ms=1200, outlines=[[station], []]),
            13: dict(hold_ms=4000, outlines=[[station], []]),
            54: dict(hold_ms=1200, outlines=[[], [station]]),
            55: dict(hold_ms=4000, outlines=[[], [station]]),
            59: dict(hold_ms=1200),
            92: dict(hold_ms=2400, outlines=[[], [station]]),
            93: dict(hold_ms=2400, outlines=[[], [[12, 61, 55, 63]]]),
            97: dict(hold_ms=2200),
        })
        scenes["verification"] = [
            dict(step=0, text="Reach the goal before energy runs out. Yellow stations refill energy, but each works only once."),
            dict(step=12, text="Schema refuels. Its current model still predicts a reusable station."),
            dict(step=13, text="Schema: the station vanishes. Verification stops the plan immediately so the model can be corrected.",
                 detail=[detail_image("Predicted", sp), detail_image("Observed", sa)]),
            dict(step=14, text="Schema resumes with a corrected rule: each refueling station is single-use."),
            dict(step=54, text="Without verification, the agent refuels at the same station and commits another plan."),
            dict(step=55, text="Without verification: the same prediction fails, but the remaining 42 actions will still execute.",
                 detail=[detail_image("Predicted", rp), detail_image("Observed", ra)]),
            dict(step=56, text="The plan continues despite the missing station."),
            dict(step=59, text="Schema is complete. The other run continues executing its incorrect plan."),
            dict(step=92, text="The agent returns to the spent station. No energy is restored."),
            dict(step=93, text="Energy reaches zero and the level resets. Execution still continues."),
            dict(step=97, text="All 42 remaining actions have executed. Only now does the agent revise its model."),
            dict(step=98, text="After the reset and correction, the agent tries again."),
            dict(step=143, text="Both runs are complete: 59 actions with Schema, 143 without verification."),
        ]

    web = {}
    for name, record in manifest.items():
        elapsed, starts = 0, []
        for duration in record["frame_durations_ms"]:
            starts.append(elapsed)
            elapsed += duration
        record["scenes"] = scenes[name]
        web[name] = dict(starts=starts, counts=[record["left"]["actions"], record["right"]["actions"]], scenes=scenes[name], segments=record.get("segments", []))
    (OUT / "full_level_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (SITE / "static/js/case-timelines.js").write_text("window.schemaCaseTimelines = " + json.dumps(web, separators=(",", ":")) + ";\n")


if __name__ == "__main__":
    main()
