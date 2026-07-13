# data_prep.R
#
# Goal: load the raw NDVI + precipitation data, and create one new
# column: the Rainfall Index.
#
# The Rainfall Index formula (same one USDA RMA uses):
#
#   Rainfall Index = (this year's precipitation / that county's own
#                      average precipitation) * 100
#
# A value of 100 means "average." Below 100 means drier than usual.
# Above 100 means wetter than usual.

# ---- Step 1: Load the data ----
# read.csv() just reads the CSV file into a table (a "data frame" in R).
panel <- read.csv("../data/ndvi_precip_panel.csv")

# Rename the "NAME" column to "county" so it's easier to read.
names(panel)[names(panel) == "NAME"] <- "county"

# ---- Step 2: Calculate each county's own average precipitation ----
# ave() computes the average of precip_mm, separately for each county
# (that's what the second argument, panel$county, tells it to group by).
# The result is the same length as the original data - each row gets
# its own county's average repeated next to it.
county_average_precip <- ave(panel$precip_mm, panel$county)

# ---- Step 3: Build the Rainfall Index ----
# This is just the formula above, applied to every row at once.
panel$rainfall_index <- (panel$precip_mm / county_average_precip) * 100

# ---- Step 4: Look at the result ----
head(panel, 10)

cat("\nNumber of rows:", nrow(panel), "\n")
cat("Number of counties:", length(unique(panel$county)), "\n")
cat("Number of years:", length(unique(panel$year)), "\n")