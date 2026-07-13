# regression_model.R

# Tests the empirical co-movement between USDA RMA's Rainfall Index (RI) -
# a real, currently operating precipitation-based insurance index - and
# NDVI (satellite-derived vegetation health), using a two-way fixed
# effects panel regression:

#   NDVI_it = alpha_i + gamma_t + beta * RI_it + epsilon_it

# where:
#   alpha_i = county fixed effects (absorb time-invariant differences:
#             soil quality, typical crop mix, baseline vegetation density)
#   gamma_t = year fixed effects (absorb statewide shocks common to all
#             counties in a given year: regional drought, hurricanes,
#             price-driven acreage shifts)
#   beta    = coefficient of interest: the within-county relationship
#             between the precipitation-based index and satellite-
#             measured vegetation health

# Standard errors are clustered by county to account for serial
# correlation in a given county's errors over time.

# Goal: test whether the Rainfall Index (built in data_prep.R) is
# related to NDVI (satellite-measured vegetation health).


# ---- Step 1: Load the fixest package ----
library(fixest)

# ---- Step 2: Run data_prep.R to get the panel data ready ----
source("data_prep.R")

# ---- Step 3: Run the regression ----
model_result <- feols(
  NDVI ~ rainfall_index | county + year,
  data = panel,
  cluster = ~county
)

# ---- Full results table ----
summary(model_result)

# ---- Important values/numbers  ----
beta <- coef(model_result)["rainfall_index"]
p_value <- pvalue(model_result)["rainfall_index"]

cat("\nRainfall Index coefficient (beta):", round(beta, 5), "\n")
cat("p-value:", round(p_value, 4), "\n")

if (p_value < 0.05) {
  cat("=> Statistically significant relationship at the 5% level.\n")
} else {
  cat("=> Not statistically significant at the 5% level.\n")
}