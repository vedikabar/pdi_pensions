# Illinois Pension Reform and Public-Sector Labor Supply

**Did Illinois' 2011 Tier 2 pension reform cause public-sector labor shortages?** 
This project estimates the causal effect of a major defined-benefit pension cut on government recruitment and retention, using a difference-in-differences design and matched CPS panel data.

## Overview

In 2011, Illinois enacted "Tier 2" pension reform, substantially reducing defined-benefit generosity for all new state and local government hires — raising the normal retirement age from 60 to 67, weakening cost-of-living adjustments, and tightening the benefit formula. This created a sharp discontinuity in compensation between otherwise similar workers based solely on hire date.

Illinois has since faced persistent public-sector labor shortages. This paper asks: did Tier 2 contribute?

**Key finding:** No detectable average effect. The post-reform shift in the Illinois recruitment differential is +0.11 pp (p = 0.858) and in retention is −3.40 pp (p = 0.240). Both are statistically indistinguishable from zero. However, the reform coincides with a structural break in the *predictability* of retention — regression R² nearly doubles post-reform — consistent with heterogeneous sorting among incumbent workers even without a detectable average treatment effect.

Results are directly relevant to the proposed Tier 2 restorations under **Senate Bill 1937**.

Prepared by the **Paul Douglas Institute** in partnership with the **Center for Tax and Budget Accountability (CTBA)**, June 2026.


## Data

- **Source:** CPS Merged Outgoing Rotation Groups (MORG), 2008–2017
- **Method:** Individuals matched across adjacent survey years using the Madrian & Lefgren (1999) protocol (household identifiers, rotation group, demographic consistency checks)
- **Sample:** ~37,000 person-year observations for recruitment; ~6,500 for retention
- **Treatment state:** Illinois | **Control states:** New York, Pennsylvania, Indiana
- Cleaned datasets are included in `data/`


## Methods

- **Two-step difference-in-differences** with year-by-year first-stage estimates and a WLS second stage
- Separate analysis for recruitment (entry into public sector) and retention (exit from public sector)
- Controls: age, sex, race/ethnicity, education, log earnings, occupation, industry, union status
- Parallel trends validated pre-reform for both margins
- Replacement rate heatmap constructed from 2025 ACFR plan parameters across all five Illinois pension systems (GARS, SERS, TRS, SURS, JRS)


## Key Results

- **Recruitment:** No significant post-reform shift (+0.11 pp, p = 0.858, 95% CI [−1.3, +1.5] pp)
- **Retention:** No significant post-reform shift (−3.40 pp, p = 0.240, 95% CI [−8.6, +1.8] pp)
- **Structural break:** Retention R² rises from ~0.10–0.13 pre-reform to ~0.25–0.29 from 2013–14 onward, suggesting compositional shifts even without an average treatment effect
- **Pension generosity:** Replacement rate analysis shows Tier 2 leaves maximum rates unchanged for career workers but significantly delays access — the mechanism most likely to affect behavior operates over 10+ year horizons, beyond this study's window


## Repo Structure

```
├── data/
│   └── cleaned/          # Cleaned CPS MORG panels, 2008–2017
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_matching_procedure.ipynb
│   ├── 03_descriptive_stats.ipynb
│   ├── 04_recruitment_analysis.ipynb
│   ├── 05_retention_analysis.ipynb
│   └── 06_replacement_rate_heatmap.ipynb
├── src/                  # Reusable scripts (matching, DiD estimation)
├── outputs/              # Figures and regression tables
├── paper/                # LaTeX source (forthcoming)
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
pip install -r requirements.txt
jupyter notebook
```

Run notebooks in order (01 → 06). Each notebook is self-contained with comments explaining the analytical choices.

---

## Citation

Baradwaj, V., Mukherjee, S., Walker, M., et al. (2026). *Illinois Pension Reform and Public Labor Force Recruitment and Retention.* Paul Douglas Institute & Center for Tax and Budget Accountability.
