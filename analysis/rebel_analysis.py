from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

DATA_PATH = Path(__file__).resolve().parent.parent / "rebel_stakes_data.csv"
SUMMARY_PATH = Path(__file__).resolve().parent / "rebel_summary.md"
REPORT_PATH = Path(__file__).resolve().parent / "rebel_report.md"
BUDGET = 100


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


FEATURE_WEIGHTS: Dict[str, float] = {
    "prime_power": 0.25,
    "last_speed": 0.20,
    "last_lp": 0.15,
    "turn_time": 0.15,
    "class_rating": 0.15,
    "fitness_flag": 0.05,
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
# Rebel Stakes Deep Dive

Technologies used: Python 3 standard library (`csv`, `dataclasses`, `pathlib`).

## Part A: Data Preparation & Feature Engineering
- **Turn Time** = Last_E2 − Last_E1. Calculated per runner.
- **Had Trouble** flag (keywords checked/steadied/blocked/wide/bumped/altered course).
- **Fitness Flag** (third off layoff pattern) = Days_Off > 45 and Last_Speed > Avg_Speed_Last_3 (none qualify in this dataset).

## Part B: Quantitative Modeling & Fair Odds
Features and weights: {FEATURE_WEIGHTS}.
Model probabilities and fair odds:

{chr(10).join(prob_lines)}

Top overlays: {', '.join(overlays) if overlays else 'None'}. Top underlays: {', '.join(underlays) if underlays else 'None'}.

## Part C: Qualitative Synthesis & Wagering
- **Upgrade (closer bias + hot pace):** {', '.join(bias_upgrade)}.
- **Downgrade (dead rail/early fade risk):** {', '.join(bias_downgrade)}.

Win bets: {win_bets[0].horse_name} and {win_bets[1].horse_name} chosen from overlay + bias-adjusted ranks.

Exacta strategy (scaled to ${BUDGET}):
{chr(10).join(exacta_lines)}
Total allocated: ${total_spend:.2f}
"""
    REPORT_PATH.write_text(report.strip() + "\n")


def main() -> None:
    horses = load_horses(DATA_PATH)
    build_scores(horses)
    write_summary(horses)
    generate_report(horses)


if __name__ == "__main__":
    main()
