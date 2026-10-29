# Forest That Lies on Paper — Green Pixels, Missing Trees

**VI:** NDVI vẫn “xanh” trong khi Hansen báo mất tán — artifact mùa/nông nghiệp vs mất rừng thật.

## Claim
NDVI / greenness can remain high while Hansen Global Forest Change reports canopy loss (seasonal crops, plantation cycles, sensor artifact). “Green on paper” ≠ standing forest.

## Research questions
- **RQ1:** In loss pixels (Hansen), what share still shows high NDVI?
- **RQ2:** How does the green-but-lost rate vary by season month in the demo?
- **RQ3:** What mismatch metric best flags “lying green” patches?

## Method
**Default demo:** synthetic rasters (NDVI field + Hansen-like loss mask) with seasonal green-up on lost patches.
**REAL_DATA:** Hansen GFC lossyear + MODIS/VIIRS NDVI for a Vietnam / SE Asia bbox — see below.

## How to run
```bash
cd forest-lies-on-paper
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/run_experiment.py
```
Outputs: `results/mismatch.csv`, `results/green_vs_loss.png`, `results/summary.json`.

## REAL_DATA steps
1. Download Hansen GFC `lossyear` / `treecover2000` for bbox (e.g. VN 8–23°N, 102–110°E) via Earth Engine or Hansen portal.
2. Download MODIS MOD13Q1 NDVI for matching dates.
3. Reproject to common grid; compute green-but-lost = (NDVI ≥ τ) ∧ (lossyear > 0).
4. Save manifests under `results/`.

## Independence
Shares **no** code or data with `ghost-carbon` or `hot-cities-blind-sensors`.
