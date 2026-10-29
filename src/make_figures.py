#!/usr/bin/env python3
"""Camera-ready figures for Forest Lies (same seed 7 rasters; numbers unchanged).

Rebuilds the 12 synthetic NDVI months exactly as run_experiment/tau_sensitivity do
and redraws Fig. 1 (green_vs_loss) and Fig. 2 (seasonal_mismatch) at 300 dpi PNG
plus PDF/SVG. Does not overwrite mismatch.csv / summary.json / tau_sensitivity.csv.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_experiment as rx  # noqa: E402

R = rx.RESULTS
OI = {"orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "yellow": "#F0E442",
      "blue": "#0072B2", "verm": "#D55E00", "purple": "#CC79A7", "black": "#000000"}
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})
PEAK_MONTH_SHOWN = 8  # same month as the original figure
TAUS = [0.5, 0.55, 0.6, 0.65, 0.7]
DRY = [1, 2, 10, 11, 12]


def save(fig, stem):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(R / f"{stem}.{ext}", dpi=300)
    plt.close(fig)


def rasters():
    rx.RNG = np.random.default_rng(7)  # reproduce main run exactly
    base, loss, agri = rx.make_basemap()
    stacks = [rx.ndvi_for_month(base, loss, agri, m) for m in range(1, 13)]
    return base, loss, agri, stacks


def green_vs_loss(loss, agri, stacks):
    nd = stacks[PEAK_MONTH_SHOWN - 1]; tau = rx.NDVI_THR
    n = nd.shape[0]
    fig, axes = plt.subplots(1, 3, figsize=(6.2, 2.55), constrained_layout=True)
    im = axes[0].imshow(nd, cmap="viridis", vmin=0, vmax=1, interpolation="nearest")
    cb = fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.02); cb.set_label("NDVI")
    axes[0].set_title(f"(a) NDVI, month {PEAK_MONTH_SHOWN}")
    cls = np.zeros(loss.shape, int); cls[loss & ~agri] = 1; cls[loss & agri] = 2
    axes[1].imshow(cls, cmap=ListedColormap(["#F2F2F2", "#555555", OI["orange"]]), vmin=0, vmax=2, interpolation="nearest")
    axes[1].set_title("(b) Synthetic loss mask")
    gl = (nd >= tau) & loss
    cls2 = np.zeros(loss.shape, int); cls2[loss] = 1; cls2[gl] = 2
    axes[2].imshow(cls2, cmap=ListedColormap(["#F2F2F2", "#BBBBBB", OI["verm"]]), vmin=0, vmax=2, interpolation="nearest")
    axes[2].set_title(f"(c) Loss ∧ NDVI ≥ {tau:g}")
    for ax in axes:
        ax.set_xticks([0, n // 2, n - 1]); ax.set_yticks([0, n // 2, n - 1]); ax.set_xlabel("x (pixels)")
    axes[0].set_ylabel("y (pixels)")
    handles = [Patch(fc="#555555", label="Loss: cleared (natural)"),
               Patch(fc=OI["orange"], label="Loss: crop-replaced"),
               Patch(fc="#BBBBBB", label="Loss, not green"),
               Patch(fc=OI["verm"], label="Loss but green (audit flag)")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.16),
               handlelength=1.4, columnspacing=1.0)
    save(fig, "green_vs_loss")


def seasonal(loss, stacks):
    months = np.arange(1, 13)
    styles = {0.5: (OI["sky"], "s", ":"), 0.55: (OI["green"], "D", "-."), 0.6: (OI["black"], "o", "-"),
              0.65: (OI["orange"], "^", "--"), 0.7: (OI["purple"], "v", (0, (1, 1)))}
    fig, ax = plt.subplots(figsize=(4.8, 3.0), constrained_layout=True)
    for m in DRY:
        ax.axvspan(m - 0.5, m + 0.5, color="#EEEEEE", lw=0, zorder=0)
    for t in TAUS:
        rates = [rx.mismatch_rate(nd, loss, thr=t)["green_but_lost_rate"] for nd in stacks]
        c, mk, ls = styles[t]
        main = abs(t - rx.NDVI_THR) < 1e-9
        ax.plot(months, rates, color=c, marker=mk, ls=ls, lw=2.0 if main else 1.1, ms=5 if main else 3.5,
                label=f"τ = {t:g}" + (" (main)" if main else ""), zorder=3 if main else 2)
    ax.set_xticks(months); ax.set_xlim(0.5, 12.5)
    ax.set_xlabel("Month (synthetic seasonal cycle; shaded = dry months)")
    ax.set_ylabel("Green-but-lost rate\nP(NDVI ≥ τ | loss)")
    ax.set_ylim(-0.02, 1.0)
    ax.yaxis.grid(True, lw=0.4, color="#dddddd"); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, loc="upper left", ncol=2, handlelength=2.2)
    save(fig, "seasonal_mismatch")


if __name__ == "__main__":
    base, loss, agri, stacks = rasters()
    green_vs_loss(loss, agri, stacks)
    seasonal(loss, stacks)
    print("wrote green_vs_loss / seasonal_mismatch .{png,pdf,svg}")
