#!/usr/bin/env python3
"""Forest Lies: NDVI greenness vs synthetic loss-mask mismatch (SYNTHETIC)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(7)
N = 96
NDVI_THR = 0.6


def make_basemap(n: int = N):
    yy, xx = np.mgrid[0:n, 0:n]
    forest = 0.75 + 0.1 * np.sin(xx / 9.0) + 0.05 * RNG.normal(size=(n, n))
    # agricultural belt (will stay green seasonally even after "loss")
    agri = ((xx > n * 0.55) & (xx < n * 0.85) & (yy > n * 0.2) & (yy < n * 0.8))
    # clear-cut patches
    loss = np.zeros((n, n), dtype=bool)
    for cy, cx, r in [(30, 40, 10), (60, 70, 12), (50, 25, 8), (70, 55, 9)]:
        loss |= (yy - cy) ** 2 + (xx - cx) ** 2 <= r**2
    # mark agri∩some forest as lost but crop-replaced
    loss |= agri & (RNG.random((n, n)) < 0.35)
    forest = np.clip(gaussian_filter(forest, 1.0), 0.1, 0.95)
    return forest, loss, agri


def ndvi_for_month(base, loss, agri, month: int) -> np.ndarray:
    """Seasonal green-up: wet-season crops on lost agri look high NDVI."""
    # month 1..12; peak green months 6-9
    season = 0.5 + 0.5 * np.sin((month - 3) / 12.0 * 2 * np.pi)
    ndvi = base.copy()
    # lost natural forest → brown
    natural_loss = loss & ~agri
    ndvi[natural_loss] = 0.25 + 0.05 * RNG.random(natural_loss.sum())
    # lost agri → seasonal crop greenness
    agri_loss = loss & agri
    ndvi[agri_loss] = 0.35 + 0.45 * season + 0.05 * RNG.random(agri_loss.sum())
    # intact forest slight seasonality
    intact = ~loss
    ndvi[intact] = np.clip(base[intact] + 0.05 * (season - 0.5), 0, 1)
    return np.clip(ndvi, 0, 1)


def mismatch_rate(ndvi, loss, thr=NDVI_THR) -> dict:
    lost = loss.sum()
    green_lost = ((ndvi >= thr) & loss).sum()
    return {
        "n_loss_pixels": int(lost),
        "n_green_and_lost": int(green_lost),
        "green_but_lost_rate": float(green_lost / max(lost, 1)),
        "mean_ndvi_on_loss": float(ndvi[loss].mean()) if lost else float("nan"),
        "mean_ndvi_intact": float(ndvi[~loss].mean()),
    }


def main():
    base, loss, agri = make_basemap()
    rows = []
    ndvi_peak = None
    for month in range(1, 13):
        ndvi = ndvi_for_month(base, loss, agri, month)
        if month == 8:
            ndvi_peak = ndvi
        m = mismatch_rate(ndvi, loss)
        m["month"] = month
        rows.append(m)
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "mismatch.csv", index=False)

    peak = df.loc[df["green_but_lost_rate"].idxmax()]
    summary = {
        "mode": "SYNTHETIC_rasters",
        "ndvi_threshold": NDVI_THR,
        "peak_month": int(peak["month"]),
        "peak_green_but_lost_rate": float(peak["green_but_lost_rate"]),
        "dry_month_rate": float(df.loc[df["month"] == 2, "green_but_lost_rate"].iloc[0]),
        "mean_rate_all_months": float(df["green_but_lost_rate"].mean()),
        "note": "Replace with Hansen GFC + MODIS NDVI for VN/SEA per README REAL_DATA",
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(df.to_string(index=False))

    assert ndvi_peak is not None
    green_lost = (ndvi_peak >= NDVI_THR) & loss
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    im0 = axes[0].imshow(ndvi_peak, cmap="YlGn", vmin=0, vmax=1)
    axes[0].set_title("NDVI (peak month)")
    plt.colorbar(im0, ax=axes[0], fraction=0.046)
    axes[1].imshow(loss, cmap="Greys")
    axes[1].set_title("Synthetic loss mask")
    axes[2].imshow(green_lost, cmap="magma")
    axes[2].set_title("Green ∩ Lost (lie pixels)")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(RESULTS / "green_vs_loss.png", dpi=120)
    plt.close()

    # seasonal curve
    fig2, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(df["month"], df["green_but_lost_rate"], marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("Green-but-lost rate")
    ax.set_title("When green pixels outlive trees")
    ax.set_xticks(range(1, 13))
    fig2.tight_layout()
    fig2.savefig(RESULTS / "seasonal_mismatch.png", dpi=120)
    plt.close()
    print(f"Wrote results under {RESULTS}")


if __name__ == "__main__":
    main()
