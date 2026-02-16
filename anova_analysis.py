import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import warnings
warnings.filterwarnings("ignore")

# ── 1. Load and clean data ──────────────────────────────────────────────
df_raw = pd.read_excel("Forage_seedlines_copy.xlsx", header=None)

headers = [
    "NAME", "REPLICATION", "PLANT_COUNT", "SEED_WEIGHT_g",
    "Avg_seed_weight_per_plant", "TOTAL_SEED_WEIGHT",
    "WET_BIOMASS_Q1", "WET_BIOMASS_Q2",
    "DRY_BIOMASS_Q1", "DRY_BIOMASS_Q2",
    "AVG_WETBM_QUAD", "AVG_WETBM_PLANT",
    "AVG_DRYBM_QUAD", "AVG_DRYBM_PLANT",
    "HARVESTED_PLANTS_Q1", "HARVESTED_PLANTS_Q2"
]

df = df_raw.iloc[2:].copy()
df.columns = headers
df.reset_index(drop=True, inplace=True)

df["NAME"] = df["NAME"].ffill()

numeric_cols = [c for c in headers if c != "NAME"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print("=" * 70)
print("         ANOVA ANALYSIS — Forage Sorghum Seedlines")
print("=" * 70)

print("\n── Cleaned Data Overview ──")
print(f"Seedlines : {df['NAME'].unique().tolist()}")
print(f"Total rows: {len(df)}  (8 seedlines × 5 replications)")
print(f"\nVariables available for analysis:")
for c in numeric_cols:
    valid = df[c].dropna()
    if len(valid) > 0:
        print(f"  {c:30s}  n={len(valid):3d}  mean={valid.mean():.2f}")

# ── 2. Select key response variables with data across all reps ──────────
anova_vars = ["PLANT_COUNT", "SEED_WEIGHT_g", "Avg_seed_weight_per_plant"]

print("\n" + "=" * 70)
print("  ONE-WAY ANOVA: Testing differences among 8 seedlines")
print("=" * 70)

for var in anova_vars:
    sub = df[["NAME", var]].dropna()
    if sub.empty:
        continue

    print(f"\n{'─' * 70}")
    print(f"  Response Variable: {var}")
    print(f"{'─' * 70}")

    # Group means
    group_stats = sub.groupby("NAME")[var].agg(["count", "mean", "std"])
    print(f"\n  Group Summary:")
    print(group_stats.to_string())

    # Normality test (Shapiro-Wilk per group)
    print(f"\n  Shapiro-Wilk Normality Test (H0: data is normal):")
    all_normal = True
    for name, group in sub.groupby("NAME"):
        vals = group[var].values
        if len(vals) >= 3:
            stat, p = stats.shapiro(vals)
            status = "Normal" if p > 0.05 else "Non-normal"
            if p <= 0.05:
                all_normal = False
            print(f"    {name:15s}  W={stat:.4f}  p={p:.4f}  ({status})")
        else:
            print(f"    {name:15s}  Too few observations (n={len(vals)})")

    # Levene's test for homogeneity of variance
    groups = [group[var].dropna().values for _, group in sub.groupby("NAME")]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) >= 2:
        lev_stat, lev_p = stats.levene(*groups)
        print(f"\n  Levene's Test for Equal Variances:")
        print(f"    W={lev_stat:.4f}  p={lev_p:.4f}  ", end="")
        print("(Equal variances)" if lev_p > 0.05 else "(Unequal variances)")

    # One-way ANOVA
    f_stat, p_val = stats.f_oneway(*groups)
    print(f"\n  *** One-Way ANOVA ***")
    print(f"    F-statistic = {f_stat:.4f}")
    print(f"    p-value     = {p_val:.6f}")
    if p_val < 0.05:
        print(f"    --> SIGNIFICANT at α=0.05: At least one seedline differs.")
    else:
        print(f"    --> NOT significant at α=0.05: No evidence of difference.")

    # ANOVA Table (Type II)
    safe_var = var.replace(" ", "_").replace("(", "").replace(")", "")
    sub_copy = sub.copy()
    sub_copy.columns = ["NAME", safe_var]
    try:
        model = ols(f'{safe_var} ~ C(NAME)', data=sub_copy).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        print(f"\n  ANOVA Table:")
        print(anova_table.to_string())
    except Exception as e:
        print(f"  (Could not build ANOVA table: {e})")

    # Tukey's HSD Post-hoc
    if p_val < 0.05:
        print(f"\n  *** Tukey's HSD Post-Hoc Test ***")
        tukey = pairwise_tukeyhsd(sub[var], sub["NAME"], alpha=0.05)
        print(tukey)

# ── 3. Biomass ANOVA (subset with biomass data) ─────────────────────────
biomass_vars = [
    ("AVG_WETBM_QUAD", "Avg Wet Biomass per Quadrant"),
    ("AVG_WETBM_PLANT", "Avg Wet Biomass per Plant"),
    ("AVG_DRYBM_QUAD", "Avg Dry Biomass per Quadrant"),
    ("AVG_DRYBM_PLANT", "Avg Dry Biomass per Plant"),
]

print("\n\n" + "=" * 70)
print("  BIOMASS ANOVA (data available for reps 2 & 4 only)")
print("=" * 70)

for var, label in biomass_vars:
    sub = df[["NAME", var]].dropna()
    if sub.empty or sub[var].nunique() < 2:
        continue

    print(f"\n{'─' * 70}")
    print(f"  Response Variable: {label} ({var})")
    print(f"{'─' * 70}")

    group_stats = sub.groupby("NAME")[var].agg(["count", "mean", "std"])
    print(f"\n  Group Summary:")
    print(group_stats.to_string())

    groups = [group[var].dropna().values for _, group in sub.groupby("NAME")]
    groups = [g for g in groups if len(g) >= 2]

    if len(groups) < 2:
        print("  Insufficient data for ANOVA (need ≥2 groups with ≥2 obs each)")
        continue

    # Levene's
    lev_stat, lev_p = stats.levene(*groups)
    print(f"\n  Levene's Test: W={lev_stat:.4f}  p={lev_p:.4f}  ", end="")
    print("(Equal)" if lev_p > 0.05 else "(Unequal)")

    # ANOVA
    f_stat, p_val = stats.f_oneway(*groups)
    print(f"\n  *** One-Way ANOVA ***")
    print(f"    F = {f_stat:.4f},  p = {p_val:.6f}")
    if p_val < 0.05:
        print(f"    --> SIGNIFICANT")
    else:
        print(f"    --> NOT significant")

    # Tukey's HSD if significant
    if p_val < 0.05:
        print(f"\n  *** Tukey's HSD Post-Hoc Test ***")
        tukey = pairwise_tukeyhsd(sub[var], sub["NAME"], alpha=0.05)
        print(tukey)

print("\n" + "=" * 70)
print("  ANALYSIS COMPLETE")
print("=" * 70)
