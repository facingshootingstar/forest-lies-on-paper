#!/usr/bin/env python3
"""tau sensitivity for green-but-lost rate on the same SYNTHETIC rasters (seed 7)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_experiment as rx

TAUS = [0.5, 0.55, 0.6, 0.65, 0.7]
rx.RNG = np.random.default_rng(7)  # reproduce main run exactly
base, loss, agri = rx.make_basemap()
stacks = [rx.ndvi_for_month(base, loss, agri, m) for m in range(1, 13)]
rows = []
for t in TAUS:
    rates = [rx.mismatch_rate(nd, loss, thr=t)["green_but_lost_rate"] for nd in stacks]
    pk = int(np.argmax(rates))
    rows.append({"tau": t, "peak_rate": rates[pk], "peak_month": pk + 1,
                 "n_months_at_peak": int(sum(abs(r - rates[pk]) < 1e-12 for r in rates)),
                 "mean_rate_all_months": float(np.mean(rates)),
                 "n_months_rate_gt_0": int(sum(r > 0 for r in rates))})
df = pd.DataFrame(rows)
df.to_csv(rx.RESULTS / "tau_sensitivity.csv", index=False)
print(df.to_string(index=False))
