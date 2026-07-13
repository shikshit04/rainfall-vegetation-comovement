# Rainfall Index and Vegetation Health Co-Movement: A Panel Analysis

A panel regression testing how closely a real USDA precipitation-based 
insurance index moves together with satellite-measured vegetation health, 
using real remote sensing and climate data for Georgia agricultural counties.

## Background: how USDA index insurance actually works

USDA's Risk Management Agency (RMA) insures pasture, rangeland, and forage 
production through two separate index insurance plans, and a producer picks 
one or the other, not both:

- **Rainfall Index (RI):** based entirely on precipitation data from NOAA's 
  Climate Prediction Center, calculated over a 0.25° x 0.25° grid 
  (roughly 17 x 17 miles). The index expresses observed precipitation as a 
  percent of the long-term average for that grid and time period, where 100 
  is average.
- **Vegetation Index (VI):** a separate RMA pilot program, available since 
  2007, that uses satellite NDVI instead of precipitation to measure 
  pasture condition.

Both plans exist because precipitation and vegetation health don't always 
agree with each other. Checking how closely they track is a real, practical 
question, and it speaks to basis risk: the chance that an index payout 
doesn't match what's actually happening on a producer's land.

## Scope note

RI and VI only insure pasture, rangeland, forage, and hay, not row crops. 
This project looks at Georgia's cotton-belt counties instead, picked using 
2023 NASS cotton acreage. This was a scope choice made for data availability 
and personal familiarity with the region, not because these counties are 
actually insured under RI/VI. Cotton is insured under a different set of 
products (Yield Protection, Revenue Protection, STAX, Area Risk Protection 
Insurance) - a companion repo re-targets this same NDVI data at those products 
instead.

## Related work

This analysis has a companion piece built in ArcGIS: [Index Insurance and Basis Risk: A GIS Illustration](https://arcg.is/0Xjn5W3), 
which covers the same basis-risk concept visually, using real Sentinel-2 imagery, land cover classification, and a computed rainfall 
index for these same Georgia counties.

## Research question

**Does satellite-measured vegetation health (NDVI) move together with a 
precipitation-based rainfall index?**

If the relationship is strong, that supports relying on the cheaper
precipitation-only index. If it's weak, that's evidence of basis risk 
between the two approaches, and a case for where satellite-based products 
could add value.

## Data sources (all real)

| Variable | Source | Description |
|---|---|---|
| NDVI | Sentinel-2 Surface Reflectance (`COPERNICUS/S2_SR_HARMONIZED`), via Google Earth Engine | Cloud-masked, growing-season (Apr-Sep) median composite; NDVI = (NIR - Red) / (NIR + Red), from bands B8 and B4 |
| Precipitation | PRISM (`OREGONSTATE/PRISM/ANm`), via Google Earth Engine | NOAA/Oregon State gridded monthly precipitation (combines PRISM's legacy AN81 and current AN91 data), summed over the same Apr-Sep window |
| County boundaries | US Census TIGER/Line (`TIGER/2018/Counties`), via Google Earth Engine | Used to aggregate NDVI and precipitation by county |

**County selection:** the 12 Georgia counties with the highest 2023 cotton 
production, per NASS county estimates (Dooly, Colquitt, Worth, Mitchell, 
Bulloch, Crisp, Brooks, Wilcox, Coffee, Irwin, Turner, Berrien). An earlier 
version of this list was picked just by geographic proximity to a smaller 
set of counties, which was replaced with this NASS-ranked version since it 
better represents the actual row-crop region.

**Time period:** 2019-2024 growing seasons, 72 county-year observations.

## Model specification
NDVI_it = alpha_i + gamma_t + beta * RI_it + epsilon_it

Where the Rainfall Index is built the same way RMA builds its own:
RI_it = (Precip_it / mean(Precip_i)) * 100

- **alpha_i** - county fixed effects: absorbs each county's normal baseline NDVI level, coming from time-invariant things like soil quality and typical crop mix.
- **gamma_t** - year fixed effects: absorbs statewide shocks common to all counties in a given year, like a regional drought or a hurricane.
- **beta** - the coefficient of interest: the within-county relationship between the precipitation index and satellite-measured vegetation health.
- **epsilon_it** - error term. Standard errors are clustered by county.

An optional interaction version (`rainfall_index * C(county)`) is included in the code to check whether this relationship varies by county, i.e. whether basis risk concentrates in certain counties rather than being spread evenly.

## Estimation

This is a fixed-effects panel design, not a causal identification strategy - there's no instrument or natural experiment being used here. Precipitation and NDVI are both outcomes of the same growing-season conditions, so this model is measuring how closely one real signal (rainfall relative to normal) tracks another (satellite-measured greenness), not claiming one causes the other. With only 12 counties, the clustered standard errors are also less reliable than they'd be with the 30-50+ clusters usually recommended for this kind of correction, which is worth keeping in mind when reading the p-value below.

## Results

**Implementation note:** this was originally built and checked in Python (`pandas`/`statsmodels`), then ported to R (`fixest`) to match the language used in the companion repo. Both give the same coefficient, which is a good sign the port is correct.

Estimated on the real panel (12 counties x 6 years, 2019-2024, n=72):

| | Estimate |
|---|---|
| Rainfall Index coefficient (beta) | 0.00035 |
| p-value | 0.115 (Python) / 0.112 (R) |
| Overall model R-squared | 0.905 |

The Rainfall Index coefficient is not significant at the 5% level. Most of the 
overall R-squared here is coming from the county and year fixed effects (17 
dummy variables), not from the rainfall index itself, so the R-squared shouldn't 
be read as the precipitation variable explaining much on its own.

Within this sample, once county differences and common year shocks are removed, 
a precipitation index doesn't show a reliable relationship with satellite-measured 
vegetation health over a full growing season. That's consistent with the reason RMA 
offers a separate Vegetation Index product in the first place - a rainfall index and 
a vegetation index aren't just interchangeable stand-ins for each other, at least not 
at this level of temporal aggregation.

A couple of caveats specific to this result: a full growing-season window may be 
masking a relationship that shows up at RMA's actual 2-month index intervals, and 
72 observations against 17 fixed-effect parameters doesn't leave a lot of 
statistical power, so a real but modest relationship could still be going undetected 
here.

Full regression output: [`outputs/regression_summary.txt`](outputs/regression_summary.txt).

## Consistency with prior literature

This lines up with existing research on the same question. Keeler and Saitone, studying basis risk in RMA's own Pasture, Rangeland, and Forage program, find that contemporaneous correlations between forage condition and precipitation in California are very poor - the same general finding as here, for the same federal program. Ballagh et al. (2012), comparing NDVI against precipitation, extreme heat, and yields across 60 US locations, found the NDVI-precipitation relationship to be highly variable and dependent on location, which matches the county-level heterogeneity this project's optional interaction model is set up to test. A broader review of satellite-based index insurance research (Adjabui et al. 2025) found vegetation-index correlations with yield losses typically land around 44-62%, with the often-quoted ~90% figure only showing up in the best individual cases - so a strong NDVI-weather relationship is more the exception than the rule in this literature. Separately, work on reducing temporal basis risk using crop phenology data (Vogel et al. 2021) argues that standard weather-index designs often miss the critical plant growth windows, which is the same limitation flagged above about this analysis using a full season instead of a 2-month interval. Put together, a weak or null RI-NDVI relationship at the county level, especially over a coarse time window, looks like the expected result here rather than a sign something went wrong.

**References:**
- Keeler, A. and Saitone, T. "Basis Risk in the Pasture, Rangeland, and Forage Insurance." UC Davis Agricultural and Resource Economics working paper.
- Ballagh, R. et al. (2012). "Applicability of the Normalized Difference Vegetation Index (NDVI) in Index-Based Crop Insurance Design." *Weather, Climate, and Society*, 4(4).
- Adjabui, D. et al. (2025). "Satellite-based data for agricultural index insurance: a systematic quantitative literature review." *Natural Hazards and Earth System Sciences*, 25.
- Vogel, J. et al. (2021). "Phenology Information Contributes to Reduce Temporal Basis Risk in Agricultural Weather Index Insurance." *Scientific Reports*.

## Repo structure
.
├── data/
│   └── ndvi_precip_panel.csv       # Real GEE export: NDVI + PRISM precip (72 rows, 2019-2024)
├── src/
│   ├── data_prep.R                  # Constructs the Rainfall Index
│   └── regression_model.R           # Two-way FE regression, clustered SE (fixest)
├── outputs/
│   └── regression_summary.txt
├── earth_engine_script.js           # The GEE script used to build the panel
├── install.R
└── LICENSE

## Running it

```r
Rscript install.R
cd src
Rscript regression_model.R
```

## License

MIT - see [LICENSE](LICENSE).