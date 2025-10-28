# Assignment 3: Run Prevention Efficiency — Balancing Pitching and Defense

## Executive Summary
Across the 2023–2024 window Milwaukee’s run prevention advantage remained defense-driven. The Brewers led this peer set in Defensive Runs Saved (52, 58) and Outs Above Average (24, 26) while keeping BABIP allowed below .280, enabling ERA to beat FIP by 0.26–0.38 runs and anchoring 92–94 win seasons without outlier strikeout totals.【F:analysis/brewers_focus_summary.csv†L1-L4】【F:data/run_prevention_2023_2024.csv†L2-L9】【F:figures/correlations.csv†L2-L7】 Sustaining glove-first roster investments delivers higher marginal value than chasing incremental stuff upgrades for 2026 planning.

## Data and Methods
- **Sample**: Brewers plus Twins, Mariners, and Rays from 2023–2024 — four comparable contenders to benchmark how pitching and fielding blend across consecutive seasons.【F:data/run_prevention_2023_2024.csv†L1-L9】【F:analysis/assignment_checklist.json†L1-L5】
- **Metrics**: Team wins, runs allowed, ERA, ERA+, FIP, WHIP, pitching WAR, BABIP allowed, DRS, UZR, OAA, and defensive WAR. Derived measures include ERA–FIP gaps, Pearson correlations, and Brewers-focused summaries for reporting.【F:data/run_prevention_2023_2024.csv†L1-L9】【F:analysis/team_run_prevention_summary.csv†L1-L9】【F:notebooks/run_prevention_analysis.py†L7-L275】
- **Tools**: A Python script loads the CSV, validates coverage for 2023–2024, exports the correlation matrix, builds a cross-season FIP vs. runs scatter, and renders DRS vs. ERA+ dual-axis bars for each season while refreshing summary tables.【F:notebooks/run_prevention_analysis.py†L92-L275】

## Key Findings
1. **Defense tracks ERA+ more tightly than raw run prevention**: DRS and OAA correlate 0.75 and 0.64 with ERA+, outpacing the -0.78 ERA+ vs. runs allowed link. BABIP allowed shows the strongest connection to runs allowed (0.75), underscoring that converting balls in play shapes outcomes in this cohort.【F:figures/correlations.csv†L2-L7】
2. **Milwaukee consistently beats FIP by pairing contact suppression with range**: The Brewers’ ERA trailed FIP by 0.38 and 0.26 runs while logging sub-.280 BABIP and the highest DRS/OAA totals, keeping actual runs allowed 20–30 tallies lower than peers with similar FIP bands.【F:analysis/brewers_focus_summary.csv†L1-L4】【F:analysis/team_run_prevention_summary.csv†L1-L9】【F:figures/fip_vs_runs_allowed.svg†L1-L7】
3. **Seasonal visuals highlight defense-driven separation**: In both 2023 and 2024 the Brewers sit below the FIP vs. runs trendline and top the DRS axis while holding ERA+ at or above Rays levels, reinforcing that gloves create their differentiating edge.【F:figures/fip_vs_runs_allowed.svg†L1-L7】【F:figures/drs_vs_era_plus_2023.svg†L1-L7】【F:figures/drs_vs_era_plus_2024.svg†L1-L7】

## Interpretation and Implications
- **Roster construction**: Twins and Mariners posted comparable FIP ranges (3.75–3.83) yet trailed Milwaukee in DRS/OAA by 15–30 plays, translating to higher runs allowed and weaker ERA+. Upgrading defense yields more marginal value than pursuing extra strikeouts for this peer group.【F:analysis/team_run_prevention_summary.csv†L1-L9】【F:figures/correlations.csv†L2-L7】
- **Pitch-to-defense fit**: Milwaukee’s BABIP allowed dipped to .279 as ground-ball leaning pitchers dominated the 2024 rotation, letting elite defenders convert contact and sustain 94 wins without radical FIP change. Maintaining that contact profile should remain a strategic priority.【F:analysis/brewers_focus_summary.csv†L1-L4】【F:notebooks/run_prevention_analysis.py†L198-L271】

## Recommendation for 2026 Planning
Prioritize sustaining elite range: extend or replace high-OAA outfielders and infield anchors, keep investing in positioning/shift optimization, and target one more ground-ball heavy starter whose batted-ball profile lets the gloves work. Supplement with bullpen swing-and-miss depth only after defensive retention, because the data show Milwaukee’s run-prevention delta stems from contact conversion more than pure velocity.【F:analysis/brewers_focus_summary.csv†L1-L4】【F:figures/correlations.csv†L2-L7】

## Visual Appendix
1. **FIP vs. Runs Allowed (2023–2024 sample)** — Aggregated scatter highlighting Brewers (outlined) across the two-season window.【F:figures/fip_vs_runs_allowed.svg†L1-L7】
2. **Run Prevention Profile Comparison (2023)** — DRS vs. ERA+ dual-axis bar chart.【F:figures/drs_vs_era_plus_2023.svg†L1-L7】
3. **Run Prevention Profile Comparison (2024)** — DRS vs. ERA+ dual-axis bar chart.【F:figures/drs_vs_era_plus_2024.svg†L1-L7】
