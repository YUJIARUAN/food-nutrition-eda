# Source data

The file `usda_foundation_2026.zip` contains the CSV archive of **USDA FoodData Central Foundation Foods, April 2026**. Original dataset: https://fdc.nal.usda.gov/download-datasets/ . The USDA materials are public-domain/CC0; credit USDA FoodData Central. The original archive filename was `FoodData_Central_foundation_food_csv_2026-04-30.zip` and was shortened for the project script.

If this file is omitted from the repository, download the **Foundation Foods — April 2026 (CSV)** ZIP from USDA, rename it to `usda_foundation_2026.zip`, and place it in this directory. Do not unzip it.

Food nutrient values are per 100 g where available. A missing nutrient record is not assumed to be zero. Energy sources 1008, 2047, and 2048 are combined in that priority order; the `energy_source` column retains which USDA definition supplied the displayed energy value. This combines several USDA energy calculation definitions and should be treated as a descriptive coverage choice, not a harmonized measurement.
