# Rebel Stakes Submission Package

This folder contains everything required by the exam deliverables and the class Brisnet context files. Regenerate the full package with:

```bash
python analysis/rebel_analysis.py
```

## Contents to Upload
- `engineered_dataset.csv` — engineered dataset with Turn_Time, Had_Trouble, Fitness_Flag, Trainer_Angle_Flag, Performance_Score, Model_Prob, Fair_Odds, Market_Odds, Value_Type.
- `rebel_report.md` — narrative memo answering Parts A1–A3, B1–B3, and C1–C3 with overlays/underlays, win bets, and exacta ticket.
- `rebel_summary.md` — sortable markdown summary table of raw inputs plus engineered features.
- `rebel_analysis.py` — documented Python workflow (csv + dataclasses) that rebuilds all outputs from `rebel_stakes_data.csv`.

## How the Workflow Works
1. Load `rebel_stakes_data.csv` (Brisnet-style fields) into the `Horse` dataclass.
2. Engineer features:
   - Turn_Time = Last_E2 − Last_E1.
   - Had_Trouble = 1 if trip note contains checked/steadied/blocked/wide/bumped/altered course.
   - Fitness_Flag = 1 when Days_Off > 45 and Last_Speed > Avg_Speed_Last_3 (third-off improver).
   - Trainer_Angle_Flag = 1 when Trainer is Brad Cox with 45–90 day gap (second-off ROI angle).
3. Compute performance scores using min–max normalized features and weights (Prime Power 0.25, Last Speed 0.20, Last LP 0.15, Turn Time 0.15, Class Rating 0.15, Fitness 0.05, Trainer Angle 0.05, Had Trouble -0.05).
4. Normalize to Model_Prob, derive Fair_Odds = 1 / Model_Prob, convert ML to Market_Odds, and tag Overlay/Underlay.
5. Export:
   - `engineered_dataset.csv` (upload-ready dataset).
   - `rebel_summary.md` (table for quick viewing).
   - `rebel_report.md` (memo with Parts A–C and wagering ticket).

## Technologies Used
Python 3 standard library (`csv`, `dataclasses`, `pathlib`) only—no external dependencies.
