"""Render MazeBench progress and Schema/Codex coverage from the paper data."""
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/schemax-matplotlib-cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
import numpy as np

SITE = Path(__file__).resolve().parents[1]
DATA = SITE.parent / "results/mazebench_figures/data/maze_data.json"
data = json.loads(DATA.read_text())
ours = data["ours"]
pick = lambda model: next(r for r in data["ai"] if r["tools"] and r["model"] == model)
codex = pick("gpt-6-astra")
SALMON, BLUE, SAGE, GRAY = "#e07a5f", "#6aa6cc", "#81b29a", "#808080"
FRAME, EMPTY = "#cbd0d6", "#f0f1f3"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "font.size": 9, "axes.labelsize": 10, "axes.titlesize": 10,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.edgecolor": FRAME, "axes.linewidth": .8,
    "axes.axisbelow": True, "figure.facecolor": "white",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
fig, axes = plt.subplots(1, 4, figsize=(11, 3.8))
fig.subplots_adjust(left=.045, right=.995, top=.79, bottom=.30, wspace=.35)
series = [
    (ours, SALMON, "Schema (GPT-6 Astra)", "-", 2),
    (codex, BLUE, "Codex (GPT-6 Astra)", "-", 1.7),
    (pick("gpt-5.6-sol"), BLUE, "Codex (GPT-5.6 Sol)", "--", 1.5),
    (pick("claude-opus-5"), SAGE, "Claude Code (Opus 5)", "-.", 1.5),
]
for col, ax in enumerate(axes[:2], start=1):
    for run, color, _, linestyle, linewidth in series:
        curve = np.asarray(run["curve"])
        ax.plot(curve[:, 0], curve[:, col], color=color, ls=linestyle, lw=linewidth)
        if run is not ours:
            ax.plot(*curve[-1, [0, col]], marker="x", ms=7, mew=2, color=color)
    ax.grid(axis="y", color="#e7e9ed", linewidth=.7)
    ax.set_xlim(0, 28000)
    ax.set_xticks([0, 10000, 20000], ["0", "10k", "20k"])
    ax.set_xlabel("Actions")
    ax.tick_params(length=0, pad=4)
axes[0].set_title("(a) Gems collected", loc="left", pad=10)
axes[0].set_ylim(0, 35)
axes[0].axhline(data["humans"]["top50_median_gems"], color=GRAY, ls=":", lw=1.2)
axes[1].set_title("(b) Rooms visited", loc="left", pad=10)
axes[1].set_ylim(0, 145)
axes[1].axhline(data["humans"]["top50_median_rooms"], color=GRAY, ls=":", lw=1.2)

letters = list("ABCDEFGHIJKLMNOP")
for ax, run, color, name, panel in [
    (axes[2], ours, SALMON, "Schema", "c"),
    (axes[3], codex, BLUE, "Codex", "d"),
]:
    grid = np.zeros((16, 16), dtype=int)
    for x, y in run["rooms_visited"]:
        grid[y, x] = 1
    count = int(grid.sum())
    assert count == run["curve"][-1][2]
    ax.imshow(grid, cmap=ListedColormap([EMPTY, color]), vmin=0, vmax=1,
              interpolation="nearest", origin="upper")
    ax.set_xticks(range(16), letters, fontsize=6)
    ax.set_yticks(range(16), letters, fontsize=6)
    ax.tick_params(which="both", length=0, pad=2)
    ax.set_xticks(np.arange(-.5, 16, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 16, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=.6)
    ax.set_title(f"({panel}) {name} room coverage\nGPT-6 Astra", pad=10)
    ax.set_xlabel(f"{count} rooms ({count / 256:.1%})", labelpad=7)
    ax.plot(7, 8, marker="o", ms=4, mfc="white", mec="#333333", mew=.8)

handles = [Line2D([], [], color=color, lw=lw, ls=ls, label=name)
           for _, color, name, ls, lw in series]
handles.append(Line2D([], [], color=GRAY, lw=1.2, ls=":", label="Human top-50 median"))
fig.legend(handles=[handles[i] for i in [0, 2, 1, 3, 4]], loc="lower center",
           bbox_to_anchor=(.52, .025), ncol=3, frameon=False, fontsize=9,
           handlelength=2.2, columnspacing=1.8, labelspacing=.6)
out = SITE / "assets/figures/maze_progress_coverage"
fig.savefig(out.with_suffix(".png"), dpi=200)
fig.savefig(out.with_suffix(".webp"), dpi=200, pil_kwargs={"lossless": True})
plt.close(fig)
print(f"Wrote {out.name}: Schema 139 rooms, Codex 113 rooms.")
