## 3. Forest That Lies on Paper

**Title:** Green Pixels, Missing Trees: When NDVI Outlives the Canopy

**Subtitle:** Do not read greenness alone as forest survival — Protocol & Synthetic Demonstration

**Abstract.**
NDVI is still used as a shortcut for “forest still there,” yet pixels can stay green after canopy loss through crops, understory or seasonality. We quantify *green-but-lost*: the share of loss-mask pixels whose NDVI stays at or above a threshold τ. On a synthetic raster suite (τ=0.6, 1535 loss pixels) the green-but-lost rate peaks at **0.60** (first reached in month 4, held through month 8), falls to 0.00 in dry months, and averages 0.30 over the year; the peak is unchanged for τ between 0.5 and 0.7. Seasonal slices show when greenness lies hardest, and a simple mismatch rate turns a vegetation map into an audit flag. A path to real loss products (Hansen Global Forest Change) plus MODIS NDVI for Vietnam/SEA is documented but not run here. We do not claim that NDVI ≠ forest is new; we package the known mismatch as a seasonal, τ-swept audit rate. **Takeaway:** green on paper is not trees on the ground. *This paper presents a reproducible audit protocol demonstrated on synthetic/proxy data; a REAL_DATA path is documented for follow-on measurement, not claimed as completed observation.*

**Keywords:** NDVI, deforestation, remote sensing validation, seasonality, greenwashing

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

**Scope note:** SYNTHETIC rasters + synthetic loss mask; Hansen GFC only in future REAL_DATA path.
