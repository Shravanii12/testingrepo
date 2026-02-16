# ANOVA Analysis Summary — Forage Sorghum Seedlines

## Objective

Determine whether statistically significant differences exist among **8 forage sorghum seedlines** across key agronomic traits.

## Seedlines Tested

P158-1R, P158-2R, P159-3R, P149-1R, Z-TR-115-12, P55-4R, D-2-3, P53-1R

- **Replications per seedline:** 5
- **Total observations:** 40

## Key Results

| Variable | F-statistic | p-value | Significant? |
|---|---|---|---|
| Plant Count | 2.5048 | 0.0359 | Yes |
| Seed Weight (g) | 1.8726 | 0.1073 | No |
| Avg Seed Weight/Plant | 1.8571 | 0.1102 | No |
| Avg Wet Biomass/Quadrant | 1.5526 | 0.2748 | No |
| Avg Wet Biomass/Plant | 1.4822 | 0.2956 | No |
| Avg Dry Biomass/Quadrant | 1.5308 | 0.2810 | No |
| Avg Dry Biomass/Plant | 1.5079 | 0.2878 | No |

## Findings

- **Plant Count** was the only variable with a significant difference (p = 0.036). Tukey's HSD showed **P55-4R (mean = 94.0)** had significantly more plants than **Z-TR-115-12 (mean = 62.0)** (p = 0.029).
- **Seed Weight** and **Avg Seed Weight per Plant** showed no significant differences among seedlines.
- **Biomass variables** were all non-significant, but only had n=2 per group (reps 2 & 4), resulting in very low statistical power.

## Files

| File | Description |
|---|---|
| `Forage_seedlines.xlsx` | Raw experimental data |
| `anova_analysis.py` | Python script for ANOVA analysis |
| `ANOVA_Report_Forage_Sorghum.docx` | Full detailed report with tables |
| `Report for Sorghum analysis (1).docx` | Original sorghum analysis report |
