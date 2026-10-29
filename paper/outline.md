# Green Pixels, Missing Trees: When NDVI Outlives the Canopy

## Abstract bullets
- NDVI can stay high after mapped forest loss (crops, seasonality); synthetic mask here, Hansen GFC only on the REAL_DATA path.
- We measure green-but-lost mismatch on synthetic (and path-to-real) rasters.
- Seasonal slices show when greenness lies hardest.
- Takeaway: do not read NDVI alone as forest survival.

## Related work & positioning (added 2026-10-29)
**Contribution.** We contribute a seasonal *audit* of green-but-lost rates `P(NDVI≥τ | loss)` as a map-quality flag, not a new deforestation detector.

**Related work & positioning.**
Hansen et al. (2013) mapped global tree-cover loss at 30 m, and Tropek et al. (2014) objected that the structural tree-cover definition counts plantations and even some crops as forest; Hansen et al. replied that the product maps tree cover, not land use. That NDVI is a weak proxy for forest is also known: Loranty et al. (2018) show NDVI/EVI do not track larch canopy cover in upland Siberia because the understory dominates the signal, and Dearborn & Baltzer (2021) find NDVI greening in a boreal peatland that is losing forest. In the wet-season tropics, low vegetation and forest are also hard to separate spectrally. Gap: these are mostly qualitative warnings; we found no reproducible metric P(NDVI≥τ∣loss) reported by month as an audit flag.

- **Not the same as Hansen et al. (2013) / Tropek et al. (2014):** we produce no forest-loss map and do not re-judge the GFC forest definition; a loss mask is an input (synthetic here, GFC only on the REAL_DATA path).
- **Not the same as Loranty et al. (2018) / Dearborn & Baltzer (2021):** we do not claim first discovery that NDVI ≠ forest; we turn that known mismatch into a single rate with a month profile and a τ sweep that any loss product can be scored with.
- **Not a deforestation detector:** green-but-lost is a map-quality flag, not a classifier.

**References.**
1. Hansen, M. C., et al. (2013). High-Resolution Global Maps of 21st-Century Forest Cover Change. Science 342, 850–853. https://doi.org/10.1126/science.1244693
2. Tropek, R., et al. (2014). Comment on “High-resolution global maps of 21st-century forest cover change”. Science 344, 981. https://doi.org/10.1126/science.1248753
3. Hansen, M. C., et al. (2014). Response to Comment on “High-resolution global maps of 21st-century forest cover change”. Science 344, 981. https://doi.org/10.1126/science.1248817
4. Loranty, M. M., et al. (2018). Vegetation Indices Do Not Capture Forest Cover Variation in Upland Siberian Larch Forests. Remote Sensing 10(11), 1686. https://doi.org/10.3390/rs10111686
5. Dearborn, K. D., Baltzer, J. L. (2021). Unexpected greening in a boreal permafrost peatland undergoing forest loss is partially attributable to tree species turnover. Global Change Biology 27(12), 2867–2882. https://doi.org/10.1111/gcb.15608

## RQs
RQ1 share of loss pixels still green; RQ2 by month; RQ3 mismatch metric.

## Method
Synthetic NDVI + loss mask; threshold τ; mismatch rate; month loop. Real path: Hansen + MODIS VN/SEA.

## Expected tables/figures
- Table 1: green-but-lost rates
- Fig 1: NDVI | loss | mismatch panels
- Table 2: by pseudo-month
