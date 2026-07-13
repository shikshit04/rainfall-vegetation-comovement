# install.R
#
# Run this once to install the packages needed to run the analysis:
#   Rscript install.R

packages <- c("dplyr", "readr", "fixest")

installed <- rownames(installed.packages())
to_install <- setdiff(packages, installed)

if (length(to_install) > 0) {
  install.packages(to_install, repos = "https://cloud.r-project.org")
} else {
  message("All required packages are already installed.")
}
