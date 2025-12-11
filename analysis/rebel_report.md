# Rebel Stakes Deep Dive (Applied Thoroughbred Racing Analytics)

**Technologies used:** Python 3 (csv, dataclasses, pathlib) for data prep, feature engineering, scoring, and report generation.

**Repro steps:** `python analysis/rebel_analysis.py` regenerates the engineered dataset, summary table, and this memo from `rebel_stakes_data.csv`.

## Deliverables Checklist (exam master list)
- **Engineered dataset:** `engineered_dataset.csv` includes Turn_Time, Had_Trouble, Fitness_Flag, Trainer_Angle_Flag, Performance_Score, Model_Prob, Fair_Odds, Market_Odds, Value_Type.
- **Calculations & model outputs:** tables below show A1–A3 flags, B1 scoring inputs, B2 normalized win probabilities, B3 fair odds, and overlay/underlay calls vs. morning line.
- **Written analysis:** this memo explicitly answers Part A (A1–A3), Part B (B1–B3 + overlays), and Part C (C1–C3) with the wagering ticket.
- **Tools list:** declared above; matches the Brisnet-style class files used in class.
- **Submission package:** engineered dataset (`engineered_dataset.csv`), tabular summary (`rebel_summary.md`), and this memo (`rebel_report.md`) for easy upload.

## Quick file map (what to upload)
- `analysis/engineered_dataset.csv` — final dataset with all engineered columns (Turn_Time, Had_Trouble, Fitness_Flag, Trainer_Angle_Flag, Performance_Score, Model_Prob, Fair_Odds, Market_Odds, Value_Type).
- `analysis/rebel_summary.md` — sortable markdown view of the field with raw + engineered features.
- `analysis/rebel_report.md` — this narrative memo with Parts A–C and wagering ticket.
- `analysis/rebel_analysis.py` — reproducible Python workflow documenting all calculations.

## Part A — Feature Engineering (A1–A3)
- **A1 Turn Time** = Last_E2 − Last_E1 (Brisnet pace structure). Higher numbers indicate a stronger far-turn move.
- **A2 Had Trouble** = 1 if the last trip note contains checked/steadied/blocked/wide/bumped/altered course (PP comment vocabulary from class handouts); otherwise 0.
- **A3 Fitness Flag** (third-off pattern) = 1 when Days_Off > 45 **and** Last_Speed > Avg_Speed_Last_3; 0 otherwise. **Trainer Angle Flag** = 1 when Trainer is Brad Cox with 45–90 Days_Off (second-off ROI angle).

Engineered variables and outcomes (Turn Time, flags, scores, probabilities, odds, value):
| Horse | Turn Time | Had Trouble | Fitness Flag | Trainer Angle | Performance Score | Model Prob | Fair Odds | Market Odds | Value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Storm Seeker | 21 | 0 | 0 | 0 | 0.746 | 0.226 | 4.43 | 11.00 | Underlay |
| Victory Light | 23 | 0 | 0 | 0 | 0.678 | 0.205 | 4.88 | 3.50 | Overlay |
| Crescent Moons | 7 | 1 | 0 | 0 | 0.632 | 0.191 | 5.23 | 7.00 | Underlay |
| Silver Verdict | 6 | 0 | 0 | 0 | 0.350 | 0.106 | 9.44 | 5.00 | Overlay |
| Odyssey King | 7 | 0 | 0 | 0 | 0.291 | 0.088 | 11.37 | 16.00 | Underlay |
| Midnight Shadow | 7 | 0 | 0 | 0 | 0.280 | 0.085 | 11.81 | 9.00 | Overlay |
| Ridge Runner | 8 | 0 | 0 | 0 | 0.256 | 0.077 | 12.91 | 13.00 | Underlay |
| Royal Banner | 14 | 1 | 0 | 0 | 0.074 | 0.022 | 44.97 | 21.00 | Overlay |

## Part B — Quantitative Modeling (B1–B3)
- **B1 Performance Score construction:** weighted linear points system using Prime Power (0.25) — composite class/pace/form anchor; Last Speed (0.20) — recency; Last LP (0.15) — finishing strength; Turn Time (0.15) — mid-race move; Class Rating (0.15) — competition faced; Fitness Flag (0.05) — improving third-off; Trainer Angle (0.05) — Brad Cox ROI edge; Had Trouble (-0.05) — penalizes compromised last trips. Each feature is min–max normalized before weighting.
- **B2 Model Probabilities:** Performance_Score values are divided by their sum to normalize to a 100% win line.
- **B3 Fair Odds:** Fair_Decimal_Odds = 1 / Model_Prob. Morning Line is converted to decimal (Market_Odds) for comparison.

Scoring outputs and odds line (with overlay/underlay calls):
| Horse | Model Prob | Fair Odds (decimal) | ML Decimal | Overlay? |
| --- | --- | --- | --- | --- |
| Storm Seeker | 0.226 | 4.43 | 11.00 | Underlay |
| Victory Light | 0.205 | 4.88 | 3.50 | Overlay |
| Crescent Moons | 0.191 | 5.23 | 7.00 | Underlay |
| Silver Verdict | 0.106 | 9.44 | 5.00 | Overlay |
| Odyssey King | 0.088 | 11.37 | 16.00 | Underlay |
| Midnight Shadow | 0.085 | 11.81 | 9.00 | Overlay |
| Ridge Runner | 0.077 | 12.91 | 13.00 | Underlay |
| Royal Banner | 0.022 | 44.97 | 21.00 | Overlay |

Top overlays: Victory Light, Midnight Shadow, Royal Banner, Silver Verdict. Top underlays: Storm Seeker, Ridge Runner, Crescent Moons, Odyssey King.

## Part C — Synthesis & Wagering (C1–C3)
- **C1 Bias/pace adjustments:**
  - **Upgrades (closer bias + projected hot pace):** Crescent Moons, Royal Banner, Odyssey King gain from the late-kick friendly flow and fading early speed.
  - **Downgrades (dead rail / early fade risk):** Midnight Shadow, Storm Seeker may be softened by the tiring front end.
- **C2 Final win bets (two horses):** Victory Light and Silver Verdict. Each is (1) near the top of the model, (2) an overlay per the fair vs. market line, and (3) positively aligned with the closer-favoring bias/pace shape.
- **C3 $100 exacta ticket:** key Victory Light on top. Secondary horses: Crescent Moons, Royal Banner, Odyssey King. Structure and stakes:
- $18.18 Exacta: Victory Light → Crescent Moons
- $18.18 Exacta: Victory Light → Royal Banner
- $18.18 Exacta: Victory Light → Odyssey King
- $9.09 Exacta saver: Crescent Moons → Victory Light
- $9.09 Exacta saver: Royal Banner → Victory Light
- $9.09 Exacta saver: Odyssey King → Victory Light
- $18.18 Exacta: Victory Light → Silver Verdict (confidence companion)
  - **Total allocated:** $100.00 (scaled to the $100 bankroll).
