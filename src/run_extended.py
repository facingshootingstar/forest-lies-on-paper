#!/usr/bin/env python3
"""Forest Lies v4 extensions: recovery of a known replanted share (positive and
negative control), observation noise, coarse/mixed pixels, and composite choice.

Self-contained (also pasted verbatim into the notebook). At rho=1 (all belt loss replanted) with no noise and
native resolution the per-seed peak/mean rates reproduce results/multi_seed.csv
exactly: same RNG call order as src/run_experiment.py. Extra noise uses a separate
generator (seed + 1000) and the replant mask uses seed + 2000, so the locked landscape is unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:  # running inside a notebook
    ROOT = Path(".")
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

N = 96
TAU = 0.6
SEEDS = list(range(7, 17))
Q_BASE = 0.35
RHO_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]   # share of belt loss replanted with crops
NOISE = [0.0, 0.02, 0.05, 0.10]
BLOCKS = [1, 4, 8]          # 8x8 blocks of 30 m ~ 240 m, close to MODIS 250 m
DRY = [1, 2, 11, 12]
WET = [5, 6, 7, 8]


def make_basemap(rng, q=Q_BASE, n=N):
    yy, xx = np.mgrid[0:n, 0:n]
    forest = 0.75 + 0.1 * np.sin(xx / 9.0) + 0.05 * rng.normal(size=(n, n))
    agri = (xx > n * 0.55) & (xx < n * 0.85) & (yy > n * 0.2) & (yy < n * 0.8)
    loss = np.zeros((n, n), dtype=bool)
    for cy, cx, r in [(30, 40, 10), (60, 70, 12), (50, 25, 8), (70, 55, 9)]:
        loss |= (yy - cy) ** 2 + (xx - cx) ** 2 <= r**2
    loss |= agri & (rng.random((n, n)) < q)
    forest = np.clip(gaussian_filter(forest, 1.0), 0.1, 0.95)
    return forest, loss, agri


def ndvi_for_month(rng, base, loss, crop, month):
    season = 0.5 + 0.5 * np.sin((month - 3) / 12.0 * 2 * np.pi)
    ndvi = base.copy()
    nat = loss & ~crop
    ndvi[nat] = 0.25 + 0.05 * rng.random(nat.sum())
    ndvi[crop] = 0.35 + 0.45 * season + 0.05 * rng.random(crop.sum())
    intact = ~loss
    ndvi[intact] = np.clip(base[intact] + 0.05 * (season - 0.5), 0, 1)
    return np.clip(ndvi, 0, 1)


def block_mean(a, b):
    if b == 1:
        return a.astype(float)
    n = a.shape[0] // b
    return a.astype(float).reshape(n, b, n, b).mean(axis=(1, 3))


def g_rate(ndvi, loss_frac, tau=TAU):
    """Area-weighted green-but-lost rate; equals the paper's G_m when b=1."""
    return float((loss_frac * (ndvi >= tau)).sum() / max(loss_frac.sum(), 1e-12))


def run(seed, rho=1.0, sigma=0.0, b=1, tau=TAU):
    rng = np.random.default_rng(seed)
    base, loss, agri = make_basemap(rng)
    crop = loss & agri
    if rho < 1:
        crop &= np.random.default_rng(seed + 2000).random(loss.shape) < rho
    stack = np.stack([ndvi_for_month(rng, base, loss, crop, m) for m in range(1, 13)])
    if sigma > 0:
        stack = np.clip(stack + np.random.default_rng(seed + 1000).normal(0, sigma, stack.shape), 0, 1)
    true_crop = float(crop.sum() / max(loss.sum(), 1))
    lf = block_mean(loss, b)
    nat_lf = block_mean(loss & ~crop, b)
    coarse = np.stack([block_mean(s, b) for s in stack])
    rates = np.array([g_rate(c, lf, tau) for c in coarse])
    nat_green = np.array([float((nat_lf * (c >= tau)).sum() / max(nat_lf.sum(), 1e-12)) for c in coarse])
    comps = dict(
        max=coarse.max(0), median=np.median(coarse, 0),
        dry=coarse[[m - 1 for m in DRY]].mean(0), wet=coarse[[m - 1 for m in WET]].mean(0),
    )
    return dict(
        seed=seed, rho=rho, sigma=sigma, block=b, n_loss=int(loss.sum()), true_crop_share=true_crop,
        peak_rate=float(rates.max()), peak_month=int(rates.argmax()) + 1, mean_rate=float(rates.mean()),
        dry_rate=float(rates[1]), nat_false_green_peak=float(nat_green.max()),
        **{f"G_{k}_composite": g_rate(v, lf, tau) for k, v in comps.items()},
        _rates=rates,
    )


def strip(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


def main():
    # 0) reproduction check against locked multi_seed.csv
    base_rows = [run(s) for s in SEEDS]
    locked = ROOT / "results" / "multi_seed.csv"
    if locked.exists():
        ms = pd.read_csv(locked).set_index("seed")
        diff = max(max(abs(d["peak_rate"] - ms.loc[d["seed"], "peak_rate"]),
                       abs(d["mean_rate"] - ms.loc[d["seed"], "mean_rate"])) for d in base_rows)
        print(f"max |diff| vs locked multi_seed.csv: {diff:.2e}")

    # 1) recovery of the known replanted share (rho=0 is the negative control),
    #    at native 30 m without noise and at 240 m with noise sd 0.05
    rec = pd.DataFrame([strip(run(s, rho=r, sigma=sg, b=b)) for (sg, b) in [(0.0, 1), (0.05, 8)]
                        for r in RHO_GRID for s in SEEDS])
    rec["abs_err"] = (rec.peak_rate - rec.true_crop_share).abs()
    rec.to_csv(RESULTS / "ext_recovery_raw.csv", index=False)
    rec_sum = rec.groupby(["block", "rho"]).agg(true_share=("true_crop_share", "mean"), peak=("peak_rate", "mean"),
                                   peak_sd=("peak_rate", "std"), max_abs_err=("abs_err", "max"),
                                   G_max=("G_max_composite", "mean"), G_dry=("G_dry_composite", "mean"), dry_rate=("dry_rate", "mean"))
    rec_sum.to_csv(RESULTS / "ext_recovery.csv")
    nat = rec[rec.block == 1]
    slope, icpt = np.polyfit(nat.true_crop_share, nat.peak_rate, 1)
    c8 = rec[rec.block == 8]
    slope8, icpt8 = np.polyfit(c8.true_crop_share, c8.peak_rate, 1)

    # 2) stressors at the locked design (rho=1): observation noise x block size
    st = pd.DataFrame([strip(run(s, sigma=sg, b=b)) for sg in NOISE for b in BLOCKS for s in SEEDS])
    st.to_csv(RESULTS / "ext_stress_raw.csv", index=False)
    st_sum = st.groupby(["sigma", "block"]).agg(
        true_share=("true_crop_share", "mean"), peak=("peak_rate", "mean"), peak_sd=("peak_rate", "std"),
        mean_rate=("mean_rate", "mean"), dry_rate=("dry_rate", "mean"),
        nat_false_green=("nat_false_green_peak", "mean"),
        G_max=("G_max_composite", "mean"), G_median=("G_median_composite", "mean"),
        G_wet=("G_wet_composite", "mean"), G_dry=("G_dry_composite", "mean"))
    st_sum["bias"] = st_sum.peak - st_sum.true_share
    st_sum.to_csv(RESULTS / "ext_stress.csv")

    # 3) composite choice at baseline (sigma 0, native) -- same verdict question, four products
    comp = st[(st.sigma == 0) & (st.block == 1)][
        ["seed", "true_crop_share", "G_max_composite", "G_median_composite", "G_wet_composite", "G_dry_composite"]]
    comp.to_csv(RESULTS / "ext_composites.csv", index=False)

    summary = dict(
        mode="SYNTHETIC_rasters_v4_extensions", tau=TAU, seeds=SEEDS, rho_grid=RHO_GRID,
        recovery_native=dict(slope=float(slope), intercept=float(icpt),
                             max_abs_err=float(nat.abs_err.max()),
                             rho0_peak_max=float(nat[nat.rho == 0].peak_rate.max())),
        recovery_240m_noise05=dict(slope=float(slope8), intercept=float(icpt8),
                                   max_abs_err=float(c8.abs_err.max()),
                                   rho0_peak_mean=float(c8[c8.rho == 0].peak_rate.mean())),
        composites_baseline={k: dict(mean=float(comp[k].mean()), sd=float(comp[k].std(ddof=1)))
                             for k in comp.columns if k.startswith("G_")},
    )
    (RESULTS / "ext_summary.json").write_text(json.dumps(summary, indent=2))

    # figure: (a) recovery, (b) peak vs block size per noise level
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    ax[0].plot([0, 1], [0, 1], color="gray", ls="--", lw=1)
    ax[0].scatter(nat.true_crop_share, nat.peak_rate, s=10, alpha=0.6, label="30 m, no noise")
    ax[0].scatter(c8.true_crop_share, c8.peak_rate, s=10, alpha=0.6, marker="s", label="240 m, noise sd 0.05")
    ax[0].legend(fontsize=7, frameon=False)
    ax[0].set_xlim(-0.02, 0.75); ax[0].set_ylim(-0.02, 0.75)
    ax[0].set_xlabel("True replanted share of loss")
    ax[0].set_ylabel("Peak green-but-lost rate")
    ax[0].set_title("(a) Recovery, 5 shares x 10 seeds", fontsize=9)
    for sg in NOISE:
        r = st_sum.xs(sg, level="sigma")
        ax[1].plot([30 * b for b in BLOCKS], r.peak, marker="o", label=f"noise sd {sg:g}")
    ax[1].axhline(st_sum.true_share.mean(), color="gray", ls="--", lw=1)
    ax[1].set_xscale("log"); ax[1].set_xticks([30 * b for b in BLOCKS], ["30 m", "120 m", "240 m"])
    ax[1].set_xlabel("Effective pixel size"); ax[1].set_ylabel("Peak rate (locked design)")
    ax[1].set_title("(b) Noise and mixed pixels", fontsize=9)
    ax[1].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(RESULTS / f"ext_recovery.{ext}", dpi=300)
    plt.close(fig)

    pd.set_option("display.width", 220)
    print(rec_sum.round(4).to_string())
    print(st_sum.round(4).to_string())
    print(comp.round(4).to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
