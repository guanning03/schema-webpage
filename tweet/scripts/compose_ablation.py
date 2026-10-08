"""Place the paper's ablation table beside its four analysis plots."""
from pathlib import Path
import hashlib
import json
import os

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WORKSPACE = ROOT.parent.parent
PLOT_SCRIPT = WORKSPACE / "results/arc3_figures/paper_fig_ablation.py"
DATA = WORKSPACE / "results/arc3_figures/data/arc_data.json"
cache = WORKSPACE / "schema-twitter/.build/plot-cache"
cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(cache))

# Build the original paper artists, without running its PDF/PNG save commands.
# Their data, labels, colors, and legends are retained below.
paper_code = PLOT_SCRIPT.read_text()
assert "\nout = " in paper_code
namespace = {"__file__": str(PLOT_SCRIPT)}
exec(compile(paper_code.split("\nout = ", 1)[0], str(PLOT_SCRIPT), "exec"), namespace)
fig = namespace["fig"]
plt = namespace["plt"]
axes = [namespace[name] for name in ("repr_ax", "cert_ax", "plan_ax", "verify_ax")]
original_series = [(line, line.get_xdata().copy(), line.get_ydata().copy())
                   for ax in axes for line in ax.lines]
original_bars = [(bar, bar.get_height()) for ax in axes for bar in ax.patches]

fig.set_size_inches(10, 6.8)
positions = [(.405, .605, .22, .33), (.755, .605, .22, .33),
             (.405, .12, .22, .33), (.755, .12, .22, .33)]
for ax, position in zip(axes, positions):
    ax.set_position(position)
    ax.title.set_fontsize(12.3)
    ax.xaxis.label.set_fontsize(11.4)
    ax.yaxis.label.set_fontsize(11.4)
    ax.tick_params(labelsize=10.5, length=3, width=.65)
    for spine in ax.spines.values():
        spine.set_linewidth(.8)
    for line in ax.lines:
        line.set_linewidth(1.8)
        line.set_markersize(3.4)
    legend = ax.get_legend()
    if legend:
        legend = ax.legend(legend.legend_handles, [text.get_text() for text in legend.get_texts()],
                           loc="lower right", fontsize=10.2, handlelength=1.25, borderaxespad=.3)
        for line in legend.get_lines():
            line.set_linewidth(1.8)
            line.set_markersize(3.4)
    for text in ax.texts:
        text.set_fontsize(8.5)

# Preserve the table as an image from the paper, at 30% of the combined width.
table_ax = fig.add_axes([.012, 0, .30, 1])
table_ax.imshow(plt.imread(ASSETS / "08-ablation.png"), interpolation="lanczos")
table_ax.set_axis_off()

for line, x, y in original_series:
    assert np.array_equal(line.get_xdata(), x) and np.array_equal(line.get_ydata(), y)
for bar, height in original_bars:
    assert bar.get_height() == height

fig.canvas.draw()
renderer = fig.canvas.get_renderer()
for ax in axes:
    texts = [ax.title, ax.xaxis.label, ax.yaxis.label,
             *ax.get_xticklabels(), *ax.get_yticklabels(), *ax.texts]
    if ax.get_legend():
        texts += ax.get_legend().get_texts()
    for text in texts:
        if text.get_visible() and text.get_text():
            box = text.get_window_extent(renderer)
            assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= fig.bbox.width and box.y1 <= fig.bbox.height, text.get_text()

output = ASSETS / "08-ablation-combined.png"
fig.savefig(output, dpi=360, facecolor="white")
plt.close(fig)
metadata = {
    "table_source": "schema-webpage/tweet/assets/08-ablation.png",
    "plot_source": str(PLOT_SCRIPT.relative_to(WORKSPACE)),
    "plot_data": str(DATA.relative_to(WORKSPACE)),
    "plot_data_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
    "layout": "Original paper table at left, 30% width; representation/certification above planning/verification at right.",
    "output_pixels": [3600, 2448],
    "notes": "Only arrangement, typography sizes, and line/marker sizes change. All plotted data, labels, legend order, and colors are retained from the paper's plotting script."
}
(ASSETS / "08-ablation-combined-provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
print(f"Exported {output.name}: 3600x2448, table plus four original analysis plots.")
