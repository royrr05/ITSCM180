# ITSCM180 Run Prevention Study

This repository contains the analysis assets for **Assignment 3: Run Prevention Efficiency — Balancing Pitching and Defense**.  The workflow has been automated end-to-end so that the 2023–2024 dataset, analytics tables, figures, and written report all stay in sync.

## Project Structure

- `data/run_prevention_2023_2024.csv` — curated pitching and fielding metrics for the Brewers plus three peer clubs (Twins, Mariners, Rays) across the 2023–2024 window.
- `notebooks/run_prevention_analysis.py` — reproducible Python script that validates assignment requirements, recomputes correlations, exports visuals, and generates summary tables referenced in the report.
- `analysis/` — auto-generated outputs, including the assignment checklist (`assignment_checklist.json`) and CSV summaries for every club and the Brewers focus table.
- `figures/` — SVG charts used in the report (FIP vs. runs allowed scatter and DRS vs. ERA+ dual-axis bars for each season).
- `reports/run_prevention_efficiency_report.md` — two-page narrative that answers the assignment prompts and cites the generated figures/tables.

## Re-running the Analysis

```bash
python notebooks/run_prevention_analysis.py
```

The command above will:

1. Verify that the dataset covers the Brewers and at least three peer teams for every season from 2023–2024.
2. Export a Pearson correlation matrix that quantifies the pitching/defense relationships.
3. Render the scatter and bar charts required by the assignment.
4. Refresh the Brewers-focused and team-wide summary tables consumed by the report.

After running the script, open `reports/run_prevention_efficiency_report.md` to review the latest narrative and reference the `figures/` outputs for the visual appendix.