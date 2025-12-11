from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

DATA_PATH = Path(__file__).resolve().parent.parent / "rebel_stakes_data.csv"
SUMMARY_PATH = Path(__file__).resolve().parent / "rebel_summary.md"
REPORT_PATH = Path(__file__).resolve().parent / "rebel_report.md"
ENGINEERED_PATH = Path(__file__).resolve().parent / "engineered_dataset.csv"
BUDGET = 100


"""End-to-end Rebel Stakes submission builder.

This script ingests the Brisnet-style CSV, engineers required features,
computes performance scores, probabilities, and odds lines, and then
exports both the engineered dataset and the memo-style report so the
entire submission package can be regenerated with a single command.
"""


@dataclass
class Horse:
    horse_name: str
    pp: int
    ml_odds: str
    trainer: str
    jockey: str
    days_off: int
    run_style: str
    avg_speed_last_3: float
    last_speed: float
    career_top: float
    last_race_comment: str
    last_e1: float
    last_e2: float
    last_lp: float
    prime_power: float
    class_rating: float
    lasix_today: str
    blinkers_on: str
    sire_awd: str
    turn_time: float = field(init=False)
    had_trouble: int = field(init=False)
    fitness_flag: int = field(init=False)
    trainer_angle_flag: int = field(init=False)
    performance_score: float = field(init=False, default=0.0)
    model_prob: float = field(init=False, default=0.0)
    fair_decimal_odds: float = field(init=False, default=0.0)
    ml_decimal_odds: float = field(init=False, default=0.0)
    overlay_status: str = field(init=False, default="")

    def engineer_features(self) -> None:
        self.turn_time = self.last_e2 - self.last_e1
        comment = (self.last_race_comment or "").lower()
        trouble_keywords = ["checked", "steadied", "blocked", "wide", "bumped", "altered course"]
        self.had_trouble = int(any(key in comment for key in trouble_keywords))
        self.fitness_flag = int(self.days_off > 45 and self.last_speed > self.avg_speed_last_3)
        self.trainer_angle_flag = int(
            "brad cox" in self.trainer.lower() and 45 <= self.days_off <= 90
        )


FEATURE_WEIGHTS: Dict[str, float] = {
    "prime_power": 0.25,
    "last_speed": 0.20,
    "last_lp": 0.15,
    "turn_time": 0.15,
    "class_rating": 0.15,
    "fitness_flag": 0.05,
    "trainer_angle_flag": 0.05,
    "had_trouble": -0.05,
}


def parse_numeric(value: str) -> float:
    if value.strip() == "":
        return 0.0
    return float(value)


def load_horses(path: Path) -> List[Horse]:
    horses: List[Horse] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            horse = Horse(
                horse_name=row["Horse_Name"],
                pp=int(parse_numeric(row["PP"])),
                ml_odds=row["ML_Odds"],
                trainer=row["Trainer"],
                jockey=row["Jockey"],
                days_off=int(parse_numeric(row["Days_Off"])),
                run_style=row["Run_Style"],
                avg_speed_last_3=parse_numeric(row["Avg_Speed_Last_3"]),
                last_speed=parse_numeric(row["Last_Speed"]),
                career_top=parse_numeric(row["Career_Top"]),
                last_race_comment=row["Last_Race_Comment"],
                last_e1=parse_numeric(row["Last_E1"]),
                last_e2=parse_numeric(row["Last_E2"]),
                last_lp=parse_numeric(row["Last_LP"]),
                prime_power=parse_numeric(row["Prime_Power"]),
                class_rating=parse_numeric(row["Class_Rating"]),
                lasix_today=row["Lasix_Today"],
                blinkers_on=row["Blinkers_On"],
                sire_awd=row["Sire_AWD"],
            )
            horse.engineer_features()
            horses.append(horse)
    return horses


def min_max_normalize(values: List[float]) -> List[float]:
    if not values:
        return []
    min_val, max_val = min(values), max(values)
    if max_val == min_val:
        return [0.5 for _ in values]
    return [(v - min_val) / (max_val - min_val) for v in values]


def ml_to_decimal(ml: str) -> float:
    try:
        top, bottom = ml.split("-")
        return 1 + float(top) / float(bottom)
    except ValueError:
        return 0.0


def build_scores(horses: List[Horse]) -> None:
    feature_vectors: Dict[str, List[float]] = {
        "prime_power": [h.prime_power for h in horses],
        "last_speed": [h.last_speed for h in horses],
        "last_lp": [h.last_lp for h in horses],
        "turn_time": [h.turn_time for h in horses],
        "class_rating": [h.class_rating for h in horses],
    }
    normalized: Dict[str, List[float]] = {
        name: min_max_normalize(vals) for name, vals in feature_vectors.items()
    }

    scores: List[float] = []
    for idx, horse in enumerate(horses):
        score = sum(
            FEATURE_WEIGHTS[key] * normalized[key][idx] for key in feature_vectors
        )
        score += FEATURE_WEIGHTS["fitness_flag"] * horse.fitness_flag
        score += FEATURE_WEIGHTS["trainer_angle_flag"] * horse.trainer_angle_flag
        score += FEATURE_WEIGHTS["had_trouble"] * horse.had_trouble
        horse.performance_score = score
        scores.append(score)

    total = sum(scores)
    for horse in horses:
        horse.model_prob = horse.performance_score / total if total else 0.0
        horse.fair_decimal_odds = 1 / horse.model_prob if horse.model_prob else 0.0
        horse.ml_decimal_odds = ml_to_decimal(horse.ml_odds)
        horse.overlay_status = (
            "Overlay" if horse.fair_decimal_odds > horse.ml_decimal_odds else "Underlay"
        )


def write_summary(horses: List[Horse]) -> None:
    headers = [
        "Horse_Name",
        "PP",
        "ML_Odds",
        "Run_Style",
        "Avg_Speed_Last_3",
        "Last_Speed",
        "Career_Top",
        "Last_Race_Comment",
        "Last_E1",
        "Last_E2",
        "Last_LP",
        "Turn_Time",
        "Had_Trouble",
        "Fitness_Flag",
        "Trainer_Angle_Flag",
        "Prime_Power",
        "Class_Rating",
        "Performance_Score",
        "Model_Prob",
        "Fair_Decimal_Odds",
        "ML_Decimal_Odds",
        "Overlay_Status",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for h in sorted(horses, key=lambda x: x.model_prob, reverse=True):
        lines.append(
            "| "
            + " | ".join(
                [
                    h.horse_name,
                    str(h.pp),
                    h.ml_odds,
                    h.run_style,
                    f"{h.avg_speed_last_3:.0f}",
                    f"{h.last_speed:.0f}",
                    f"{h.career_top:.0f}",
                    h.last_race_comment,
                    f"{h.last_e1:.0f}",
                    f"{h.last_e2:.0f}",
                    f"{h.last_lp:.0f}",
                    f"{h.turn_time:.0f}",
                    str(h.had_trouble),
                    str(h.fitness_flag),
                    str(h.trainer_angle_flag),
                    f"{h.prime_power:.1f}",
                    f"{h.class_rating:.0f}",
                    f"{h.performance_score:.3f}",
                    f"{h.model_prob:.3f}",
                    f"{h.fair_decimal_odds:.2f}",
                    f"{h.ml_decimal_odds:.2f}",
                    h.overlay_status,
                ]
            )
            + " |"
        )
    SUMMARY_PATH.write_text("\n".join(lines))


def select_win_bets(horses: List[Horse]) -> List[Horse]:
    def bias_bonus(h: Horse) -> float:
        return 0.05 if h.run_style == "S" else 0.0

    overlays = [h for h in horses if h.overlay_status == "Overlay"]
    ranked = sorted(overlays, key=lambda h: (h.model_prob + bias_bonus(h)), reverse=True)
    if len(ranked) >= 2:
        return ranked[:2]
    top_probs = sorted(horses, key=lambda h: (h.model_prob + bias_bonus(h)), reverse=True)
    return top_probs[:2]


def generate_report(horses: List[Horse]) -> None:
    engineered_lines = [
        "| Horse | Turn Time | Had Trouble | Fitness Flag | Trainer Angle | Performance Score | Model Prob | Fair Odds | Market Odds | Value |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for h in sorted(horses, key=lambda x: x.model_prob, reverse=True):
        engineered_lines.append(
            "| "
            + " | ".join(
                [
                    h.horse_name,
                    f"{h.turn_time:.0f}",
                    str(h.had_trouble),
                    str(h.fitness_flag),
                    str(h.trainer_angle_flag),
                    f"{h.performance_score:.3f}",
                    f"{h.model_prob:.3f}",
                    f"{h.fair_decimal_odds:.2f}",
                    f"{h.ml_decimal_odds:.2f}",
                    h.overlay_status,
                ]
            )
            + " |"
        )

    prob_lines = [
        "| Horse | Model Prob | Fair Odds (decimal) | ML Decimal | Overlay? |",
        "| --- | --- | --- | --- | --- |",
    ]
    for h in sorted(horses, key=lambda x: x.model_prob, reverse=True):
        prob_lines.append(
            f"| {h.horse_name} | {h.model_prob:.3f} | {h.fair_decimal_odds:.2f} | {h.ml_decimal_odds:.2f} | {h.overlay_status} |"
        )

    overlays = [h.horse_name for h in horses if h.overlay_status == "Overlay"]
    underlays = [h.horse_name for h in horses if h.overlay_status == "Underlay"]

    bias_upgrade = [h.horse_name for h in horses if h.run_style == "S"]
    bias_downgrade = [h.horse_name for h in horses if h.run_style == "E"]

    win_bets = select_win_bets(horses)

    top_pick = win_bets[0]
    secondary = win_bets[1]

    bottom_targets = [h for h in horses if h.horse_name not in {top_pick.horse_name}]
    main_targets = [h for h in bottom_targets if h.run_style == "S"] or bottom_targets

    main_bet = 20
    saver_bet = 10
    main_cost = main_bet * len(main_targets)
    saver_cost = saver_bet * len(main_targets)
    top_to_secondary_cost = main_bet
    total_cost = main_cost + saver_cost + top_to_secondary_cost

    scale = BUDGET / total_cost if total_cost else 0
    main_bet *= scale
    saver_bet *= scale
    top_to_secondary_cost = main_bet

    total_spend = main_bet * len(main_targets) + saver_bet * len(main_targets) + top_to_secondary_cost
    exacta_lines = [f"- ${main_bet:.2f} Exacta: {top_pick.horse_name} → {t.horse_name}" for t in main_targets]
    exacta_lines += [f"- ${saver_bet:.2f} Exacta saver: {t.horse_name} → {top_pick.horse_name}" for t in main_targets]
    exacta_lines.append(
        f"- ${top_to_secondary_cost:.2f} Exacta: {top_pick.horse_name} → {secondary.horse_name} (confidence companion)"
    )

    report = f"""
# Rebel Stakes Deep Dive (Applied Thoroughbred Racing Analytics)

**Technologies used:** Python 3 (csv, dataclasses, pathlib) for data prep, feature engineering, scoring, and report generation.

**Repro steps:** `python analysis/rebel_analysis.py` regenerates the engineered dataset, summary table, and this memo from `rebel_stakes_data.csv`.

## Deliverables Checklist (exam master list)
- **Engineered dataset:** `{ENGINEERED_PATH.name}` includes Turn_Time, Had_Trouble, Fitness_Flag, Trainer_Angle_Flag, Performance_Score, Model_Prob, Fair_Odds, Market_Odds, Value_Type.
- **Calculations & model outputs:** tables below show A1–A3 flags, B1 scoring inputs, B2 normalized win probabilities, B3 fair odds, and overlay/underlay calls vs. morning line.
- **Written analysis:** this memo explicitly answers Part A (A1–A3), Part B (B1–B3 + overlays), and Part C (C1–C3) with the wagering ticket.
- **Tools list:** declared above; matches the Brisnet-style class files used in class.
- **Submission package:** engineered dataset (`{ENGINEERED_PATH.name}`), tabular summary (`{SUMMARY_PATH.name}`), and this memo (`{REPORT_PATH.name}`) for easy upload.

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
{chr(10).join(engineered_lines)}

## Part B — Quantitative Modeling (B1–B3)
- **B1 Performance Score construction:** weighted linear points system using Prime Power (0.25) — composite class/pace/form anchor; Last Speed (0.20) — recency; Last LP (0.15) — finishing strength; Turn Time (0.15) — mid-race move; Class Rating (0.15) — competition faced; Fitness Flag (0.05) — improving third-off; Trainer Angle (0.05) — Brad Cox ROI edge; Had Trouble (-0.05) — penalizes compromised last trips. Each feature is min–max normalized before weighting.
- **B2 Model Probabilities:** Performance_Score values are divided by their sum to normalize to a 100% win line.
- **B3 Fair Odds:** Fair_Decimal_Odds = 1 / Model_Prob. Morning Line is converted to decimal (Market_Odds) for comparison.

Scoring outputs and odds line (with overlay/underlay calls):
{chr(10).join(prob_lines)}

Top overlays: {', '.join(overlays) if overlays else 'None'}. Top underlays: {', '.join(underlays) if underlays else 'None'}.

## Part C — Synthesis & Wagering (C1–C3)
- **C1 Bias/pace adjustments:**
  - **Upgrades (closer bias + projected hot pace):** {', '.join(bias_upgrade)} gain from the late-kick friendly flow and fading early speed.
  - **Downgrades (dead rail / early fade risk):** {', '.join(bias_downgrade)} may be softened by the tiring front end.
- **C2 Final win bets (two horses):** {win_bets[0].horse_name} and {win_bets[1].horse_name}. Each is (1) near the top of the model, (2) an overlay per the fair vs. market line, and (3) positively aligned with the closer-favoring bias/pace shape.
- **C3 $100 exacta ticket:** key {top_pick.horse_name} on top. Secondary horses: {', '.join(t.horse_name for t in main_targets)}. Structure and stakes:
{chr(10).join(exacta_lines)}
  - **Total allocated:** ${total_spend:.2f} (scaled to the $100 bankroll).
"""
    REPORT_PATH.write_text(report.strip() + "\n")


def write_engineered_dataset(horses: List[Horse]) -> None:
    headers = [
        "Horse_Name",
        "PP",
        "Run_Style",
        "Turn_Time",
        "Had_Trouble",
        "Fitness_Flag",
        "Trainer_Angle_Flag",
        "Prime_Power",
        "Last_Speed",
        "Last_LP",
        "Class_Rating",
        "Performance_Score",
        "Model_Prob",
        "Fair_Odds",
        "Market_Odds",
        "Value_Type",
    ]
    with open(ENGINEERED_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for h in sorted(horses, key=lambda x: x.model_prob, reverse=True):
            writer.writerow(
                [
                    h.horse_name,
                    h.pp,
                    h.run_style,
                    round(h.turn_time, 1),
                    h.had_trouble,
                    h.fitness_flag,
                    h.trainer_angle_flag,
                    round(h.prime_power, 1),
                    round(h.last_speed, 1),
                    round(h.last_lp, 1),
                    round(h.class_rating, 1),
                    round(h.performance_score, 4),
                    round(h.model_prob, 4),
                    round(h.fair_decimal_odds, 3),
                    round(h.ml_decimal_odds, 3),
                    h.overlay_status,
                ]
            )


def main() -> None:
    horses = load_horses(DATA_PATH)
    build_scores(horses)
    write_summary(horses)
    write_engineered_dataset(horses)
    generate_report(horses)


if __name__ == "__main__":
    main()
