"""
regression_model.py

Tests the empirical co-movement between USDA RMA's Rainfall Index (RI) —
a real, currently operating precipitation-based insurance index — and
NDVI (satellite-derived vegetation health), using a two-way fixed
effects panel regression:

    NDVI_it = alpha_i + gamma_t + beta * RI_it + epsilon_it

where:
    alpha_i = county fixed effects (absorb time-invariant differences:
              soil quality, typical crop mix, baseline vegetation density)
    gamma_t = year fixed effects (absorb statewide shocks common to all
              counties in a given year: regional drought, hurricanes,
              price-driven acreage shifts)
    beta    = coefficient of interest: the within-county relationship
              between the precipitation-based index and satellite-
              measured vegetation health

Standard errors are clustered by county to account for serial
correlation in a given county's errors over time.

IMPORTANT SCOPE NOTE: this is an associational/descriptive fixed-effects
design, not a causal identification strategy (no instrument, no natural
experiment). See README.md for the full discussion of this distinction.
"""

import pandas as pd
import statsmodels.formula.api as smf

from data_prep import load_panel, build_rainfall_index


def run_regression(panel: pd.DataFrame):
    model = smf.ols(
        formula="NDVI ~ rainfall_index + C(county) + C(year)",
        data=panel
    )
    result = model.fit(
        cov_type="cluster",
        cov_kwds={"groups": panel["county"]}
    )
    return result


def run_interaction_model(panel: pd.DataFrame, group_col: str = "county"):
    """
    Optional heterogeneity check: allows the RI-NDVI slope to vary by
    group. With only 12 counties x 6 years, interacting with every
    individual county leaves too few degrees of freedom to trust
    individual estimates - see README for this caveat. Included here
    for completeness / as a template for a larger sample.
    """
    model = smf.ols(
        formula=f"NDVI ~ rainfall_index * C({group_col}) + C(year)",
        data=panel
    )
    result = model.fit(
        cov_type="cluster",
        cov_kwds={"groups": panel["county"]}
    )
    return result


if __name__ == "__main__":
    panel = load_panel()
    panel = build_rainfall_index(panel)

    print("=== Main model: NDVI ~ Rainfall Index (two-way FE, clustered SE) ===\n")
    main_result = run_regression(panel)
    print(main_result.summary())

    beta = main_result.params["rainfall_index"]
    pval = main_result.pvalues["rainfall_index"]
    print(f"\nRainfall Index coefficient (beta): {beta:.5f}")
    print(f"p-value: {pval:.4f}")
    if pval < 0.05:
        print("=> Statistically significant co-movement between RI and NDVI at 5% level.")
    else:
        print("=> No statistically significant co-movement detected at 5% level.")
