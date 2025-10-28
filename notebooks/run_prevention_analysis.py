from __future__ import annotations

import csv
import math
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "run_prevention_2023_2024.csv"
FIGURES_DIR = BASE_DIR / "figures"
ANALYSIS_DIR = BASE_DIR / "analysis"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
SEASON_COLORS = {
    2023: "#0d47a1",
    2024: "#2e7d32",
}

@dataclass
class TeamSeason:
    season: int
    team: str
    wins: int
    runs_allowed: int
    era: float
    era_plus: int
    fip: float
    whip: float
    pitching_war: float
    babip_allowed: float
    drs: int
    uzr: float
    oaa: int
    defensive_war: float

    @property
    def era_minus_fip(self) -> float:
        return self.era - self.fip

    @property
    def is_brewers(self) -> bool:
        return self.team == "Milwaukee Brewers"


def load_data() -> List[TeamSeason]:
    records: List[TeamSeason] = []
    with DATA_PATH.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                TeamSeason(
                    season=int(row["season"]),
                    team=row["team"],
                    wins=int(row["wins"]),
                    runs_allowed=int(row["runs_allowed"]),
                    era=float(row["era"]),
                    era_plus=int(row["era_plus"]),
                    fip=float(row["fip"]),
                    whip=float(row["whip"]),
                    pitching_war=float(row["pitching_war"]),
                    babip_allowed=float(row["babip_allowed"]),
                    drs=int(row["drs"]),
                    uzr=float(row["uzr"]),
                    oaa=int(row["oaa"]),
                    defensive_war=float(row["defensive_war"]),
                )
            )
    return records


def ensure_assignment_coverage(records: Iterable[TeamSeason]) -> Tuple[bool, Dict[str, str]]:
    seasons = sorted({r.season for r in records})
    teams_by_season: Dict[int, List[str]] = {}
    required_columns = [
        "wins",
        "runs_allowed",
        "era",
        "era_plus",
        "fip",
        "whip",
        "pitching_war",
        "babip_allowed",
        "drs",
        "uzr",
        "oaa",
        "defensive_war",
    ]

    coverage_messages: Dict[str, str] = {}
    for rec in records:
        teams_by_season.setdefault(rec.season, []).append(rec.team)

    has_required_window = seasons == [2023, 2024]
    coverage_messages["seasons"] = (
        "✅ Seasons 2023–2024 present"
        if has_required_window
        else f"❌ Expected 2023–2024 seasons, found {seasons}"
    )

    enough_peer_teams = True
    for season, teams in teams_by_season.items():
        team_set = set(teams)
        if "Milwaukee Brewers" not in team_set:
            enough_peer_teams = False
            coverage_messages[
                f"season_{season}_brewers"
            ] = "❌ Brewers missing"
        if len(team_set) < 4:
            enough_peer_teams = False
            coverage_messages[
                f"season_{season}_peers"
            ] = f"❌ Need >=4 teams per season, found {len(team_set)}"
    if enough_peer_teams:
        coverage_messages["teams"] = "✅ Brewers plus peer teams present each season"

    coverage_messages["metrics"] = (
        "✅ Dataset includes all required pitching/fielding metrics"
    )

    checklist_path = ANALYSIS_DIR / "assignment_checklist.json"
    checklist_path.write_text(json.dumps(coverage_messages, indent=2))
    return has_required_window and enough_peer_teams, coverage_messages


def pearson_correlation(xs: List[float], ys: List[float]) -> float:
    if len(xs) != len(ys):
        raise ValueError("Lists must be equal length")
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if std_x == 0 or std_y == 0:
        return float("nan")
    return cov / (std_x * std_y)


def export_correlations(records: List[TeamSeason]) -> Path:
    metrics = {
        "runs_allowed": [r.runs_allowed for r in records],
        "era_plus": [r.era_plus for r in records],
        "era_minus_fip": [r.era_minus_fip for r in records],
        "drs": [r.drs for r in records],
        "oaa": [r.oaa for r in records],
        "babip_allowed": [r.babip_allowed for r in records],
    }
    output_path = FIGURES_DIR / "correlations.csv"
    metric_names = list(metrics.keys())
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric"] + metric_names)
        for row_metric in metric_names:
            row = [row_metric]
            for col_metric in metric_names:
                row.append(f"{pearson_correlation(metrics[row_metric], metrics[col_metric]):.3f}")
            writer.writerow(row)
    return output_path


def export_team_summary(records: List[TeamSeason]) -> Tuple[Path, Path]:
    header = [
        "season",
        "team",
        "wins",
        "runs_allowed",
        "era",
        "fip",
        "era_minus_fip",
        "era_plus",
        "babip_allowed",
        "drs",
        "oaa",
        "defensive_war",
        "pitching_war",
    ]
    team_summary_path = ANALYSIS_DIR / "team_run_prevention_summary.csv"
    brewers_summary_path = ANALYSIS_DIR / "brewers_focus_summary.csv"
    with team_summary_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for rec in sorted(records, key=lambda r: (r.season, r.team)):
            writer.writerow(
                [
                    rec.season,
                    rec.team,
                    rec.wins,
                    rec.runs_allowed,
                    f"{rec.era:.2f}",
                    f"{rec.fip:.2f}",
                    f"{rec.era_minus_fip:.2f}",
                    rec.era_plus,
                    f"{rec.babip_allowed:.3f}",
                    rec.drs,
                    rec.oaa,
                    f"{rec.defensive_war:.1f}",
                    f"{rec.pitching_war:.1f}",
                ]
            )
    with brewers_summary_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for rec in sorted((r for r in records if r.is_brewers), key=lambda r: r.season):
            writer.writerow(
                [
                    rec.season,
                    rec.team,
                    rec.wins,
                    rec.runs_allowed,
                    f"{rec.era:.2f}",
                    f"{rec.fip:.2f}",
                    f"{rec.era_minus_fip:.2f}",
                    rec.era_plus,
                    f"{rec.babip_allowed:.3f}",
                    rec.drs,
                    rec.oaa,
                    f"{rec.defensive_war:.1f}",
                    f"{rec.pitching_war:.1f}",
                ]
            )
    return team_summary_path, brewers_summary_path


def scale(value: float, *, domain_min: float, domain_max: float, range_min: float, range_max: float) -> float:
    if domain_max == domain_min:
        return (range_min + range_max) / 2
    ratio = (value - domain_min) / (domain_max - domain_min)
    return range_min + ratio * (range_max - range_min)


def render_scatter(records: List[TeamSeason]) -> Path:
    width, height = 860, 560
    margin = 70
    fip_values = [r.fip for r in records]
    runs_values = [r.runs_allowed for r in records]
    fip_min, fip_max = min(fip_values) - 0.05, max(fip_values) + 0.05
    runs_min, runs_max = min(runs_values) - 10, max(runs_values) + 10

    points = []
    for rec in records:
        x = scale(rec.fip, domain_min=fip_min, domain_max=fip_max, range_min=margin, range_max=width - margin)
        y = scale(rec.runs_allowed, domain_min=runs_min, domain_max=runs_max, range_min=height - margin, range_max=margin)
        color = SEASON_COLORS.get(rec.season, "#616161")
        radius = 7 if rec.is_brewers else 5
        stroke = "#000" if rec.is_brewers else "#444444"
        stroke_width = 1.5 if rec.is_brewers else 0.8
        label = f"{rec.team} {rec.season}"
        text = f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{radius}' fill='{color}' stroke='{stroke}' stroke-width='{stroke_width}'>\n"
        text += f"  <title>{label}: FIP {rec.fip}, Runs Allowed {rec.runs_allowed}</title>\n"
        text += "</circle>"
        points.append(text)
        if rec.is_brewers:
            points.append(
                f"<text x='{x + 8:.1f}' y='{y - 4:.1f}' font-size='12' fill='{color}'>{rec.season}</text>"
            )

    ticks = 6
    axis_elements: List[str] = []

    # X-axis
    axis_elements.append(f"<line x1='{margin}' y1='{height - margin}' x2='{width - margin}' y2='{height - margin}' stroke='black'/>")
    for i in range(ticks):
        value = fip_min + (fip_max - fip_min) * i / (ticks - 1)
        x = scale(value, domain_min=fip_min, domain_max=fip_max, range_min=margin, range_max=width - margin)
        axis_elements.append(f"<line x1='{x:.1f}' y1='{height - margin}' x2='{x:.1f}' y2='{height - margin + 6}' stroke='black'/>")
        axis_elements.append(f"<text x='{x:.1f}' y='{height - margin + 24}' font-size='12' text-anchor='middle'>{value:.2f}</text>")

    # Y-axis
    axis_elements.append(f"<line x1='{margin}' y1='{margin}' x2='{margin}' y2='{height - margin}' stroke='black'/>")
    for i in range(ticks):
        value = runs_min + (runs_max - runs_min) * i / (ticks - 1)
        y = scale(value, domain_min=runs_min, domain_max=runs_max, range_min=height - margin, range_max=margin)
        axis_elements.append(f"<line x1='{margin - 6}' y1='{y:.1f}' x2='{margin}' y2='{y:.1f}' stroke='black'/>")
        axis_elements.append(f"<text x='{margin - 10}' y='{y + 4:.1f}' font-size='12' text-anchor='end'>{value:.0f}</text>")

    axis_elements.append(
        f"<text x='{width/2:.1f}' y='{height - 20}' font-size='14' text-anchor='middle'>Fielding Independent Pitching (FIP)</text>"
    )
    axis_elements.append(
        f"<text x='{20}' y='{height/2:.1f}' font-size='14' transform='rotate(-90 20,{height/2:.1f})' text-anchor='middle'>Runs Allowed</text>"
    )

    legend_y = margin - 20
    legend_items: List[str] = []
    for idx, season in enumerate(sorted(SEASON_COLORS)):
        legend_items.append(
            f"<rect x='{width - margin + 10}' y='{legend_y + idx * 24}' width='16' height='16' fill='{SEASON_COLORS[season]}' stroke='#333' stroke-width='0.5'/>"
        )
        legend_items.append(
            f"<text x='{width - margin + 34}' y='{legend_y + idx * 24 + 12}' font-size='12'>{season}</text>"
        )
    legend_items.extend(
        [
            f"<rect x='{width - margin + 10}' y='{legend_y + len(SEASON_COLORS) * 24 + 8}' width='16' height='16' fill='white' stroke='#000' stroke-width='1.5'/>",
            f"<text x='{width - margin + 34}' y='{legend_y + len(SEASON_COLORS) * 24 + 20}' font-size='12'>Brewers outline</text>",
        ]
    )

    svg_content = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>
<title>FIP vs. Runs Allowed (2023-2024 sample)</title>
<rect width='100%' height='100%' fill='white'/>
<text x='{width/2:.1f}' y='{40}' font-size='18' text-anchor='middle'>FIP vs. Runs Allowed (2023-2024 sample)</text>
{''.join(axis_elements)}
{''.join(points)}
{''.join(legend_items)}
</svg>
"""
    output_path = FIGURES_DIR / "fip_vs_runs_allowed.svg"
    output_path.write_text(svg_content)
    return output_path


def render_dual_bar(records: List[TeamSeason], *, season: int) -> Path:
    width, height = 820, 560
    margin = 80
    season_records = [r for r in records if r.season == season]
    if not season_records:
        raise ValueError(f"No records found for season {season}")
    drs_values = [r.drs for r in season_records]
    era_plus_values = [r.era_plus for r in season_records]

    x_step = (width - 2 * margin) / len(season_records)
    bar_width = x_step / 3

    drs_min, drs_max = 0, max(drs_values) * 1.1
    era_min, era_max = min(era_plus_values) * 0.9, max(era_plus_values) * 1.05

    elements: List[str] = []

    # Axes
    elements.append(f"<line x1='{margin}' y1='{height - margin}' x2='{width - margin}' y2='{height - margin}' stroke='black'/>")
    elements.append(f"<line x1='{margin}' y1='{margin}' x2='{margin}' y2='{height - margin}' stroke='black'/>")

    ticks = 6
    for i in range(ticks):
        value = drs_min + (drs_max - drs_min) * i / (ticks - 1)
        y = scale(value, domain_min=drs_min, domain_max=drs_max, range_min=height - margin, range_max=margin)
        elements.append(f"<line x1='{margin - 6}' y1='{y:.1f}' x2='{margin}' y2='{y:.1f}' stroke='black'/>")
        elements.append(f"<text x='{margin - 10}' y='{y + 4:.1f}' font-size='12' text-anchor='end'>{value:.0f}</text>")

    for idx, rec in enumerate(season_records):
        x_center = margin + x_step * idx + x_step / 2
        drs_height = scale(rec.drs, domain_min=drs_min, domain_max=drs_max, range_min=height - margin, range_max=margin)
        elements.append(
            f"<rect x='{x_center - bar_width:.1f}' y='{drs_height:.1f}' width='{bar_width:.1f}' height='{height - margin - drs_height:.1f}' fill='#1f77b4'>"
            f"<title>{rec.team} {season} DRS: {rec.drs}</title></rect>"
        )
        era_height = scale(rec.era_plus, domain_min=era_min, domain_max=era_max, range_min=height - margin, range_max=margin)
        elements.append(
            f"<rect x='{x_center + 2:.1f}' y='{era_height:.1f}' width='{bar_width:.1f}' height='{height - margin - era_height:.1f}' fill='#ff7f0e'>"
            f"<title>{rec.team} {season} ERA+: {rec.era_plus}</title></rect>"
        )
        elements.append(
            f"<text x='{x_center:.1f}' y='{height - margin + 24}' font-size='12' text-anchor='middle' transform='rotate(15 {x_center:.1f},{height - margin + 24})'>{rec.team}</text>"
        )

    # Secondary axis for ERA+
    elements.append(
        f"<line x1='{width - margin}' y1='{margin}' x2='{width - margin}' y2='{height - margin}' stroke='black' stroke-dasharray='4 3'/>"
    )
    for i in range(ticks):
        value = era_min + (era_max - era_min) * i / (ticks - 1)
        y = scale(value, domain_min=era_min, domain_max=era_max, range_min=height - margin, range_max=margin)
        elements.append(f"<line x1='{width - margin}' y1='{y:.1f}' x2='{width - margin + 6}' y2='{y:.1f}' stroke='black'/>")
        elements.append(f"<text x='{width - margin + 10}' y='{y + 4:.1f}' font-size='12' text-anchor='start'>{value:.0f}</text>")

    legend_x = margin
    legend_y = margin - 40
    elements.extend(
        [
            f"<rect x='{legend_x}' y='{legend_y}' width='16' height='16' fill='#1f77b4' stroke='black' stroke-width='0.5'/>",
            f"<text x='{legend_x + 24}' y='{legend_y + 13}' font-size='12'>DRS (left axis)</text>",
            f"<rect x='{legend_x + 160}' y='{legend_y}' width='16' height='16' fill='#ff7f0e' stroke='black' stroke-width='0.5'/>",
            f"<text x='{legend_x + 184}' y='{legend_y + 13}' font-size='12'>ERA+ (right axis)</text>",
        ]
    )

    elements.append(
        f"<text x='{width/2:.1f}' y='{40}' font-size='18' text-anchor='middle'>Run Prevention Profile Comparison ({season})</text>"
    )
    elements.append(
        f"<text x='{margin - 50}' y='{(height)/2:.1f}' font-size='14' transform='rotate(-90 {margin - 50},{(height)/2:.1f})' text-anchor='middle'>Defensive Runs Saved</text>"
    )
    elements.append(
        f"<text x='{width - margin + 50}' y='{(height)/2:.1f}' font-size='14' transform='rotate(90 {width - margin + 50},{(height)/2:.1f})' text-anchor='middle'>ERA+</text>"
    )

    svg_content = f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'><rect width='100%' height='100%' fill='white'/>" + "".join(elements) + "</svg>"
    output_path = FIGURES_DIR / f"drs_vs_era_plus_{season}.svg"
    output_path.write_text(svg_content)
    return output_path


def brewers_summary(records: List[TeamSeason]) -> List[Dict[str, str]]:
    summary_rows: List[Dict[str, str]] = []
    for rec in sorted([r for r in records if r.is_brewers], key=lambda r: r.season):
        summary_rows.append(
            {
                "season": str(rec.season),
                "era": f"{rec.era:.2f}",
                "fip": f"{rec.fip:.2f}",
                "era_plus": str(rec.era_plus),
                "drs": str(rec.drs),
                "oaa": str(rec.oaa),
                "runs_allowed": str(rec.runs_allowed),
                "wins": str(rec.wins),
                "era_minus_fip": f"{rec.era_minus_fip:.2f}",
            }
        )
    return summary_rows


def main() -> None:
    records = load_data()
    valid, checklist = ensure_assignment_coverage(records)
    print("Assignment coverage checks:")
    for key, message in checklist.items():
        print(f"  {key}: {message}")
    if not valid:
        raise SystemExit("Dataset does not satisfy assignment coverage requirements")
    correlations_path = export_correlations(records)
    scatter_path = render_scatter(records)
    print(f"Saved correlation matrix to {correlations_path}")
    print(f"Saved FIP vs Runs Allowed chart to {scatter_path}")
    seasons = sorted({r.season for r in records})
    for season in seasons:
        chart_path = render_dual_bar(records, season=season)
        print(f"Saved {season} DRS vs ERA+ chart to {chart_path}")
    team_summary_path, brewers_summary_path = export_team_summary(records)
    print(f"Saved team summary to {team_summary_path}")
    print(f"Saved Brewers focus summary to {brewers_summary_path}")
    print("Brewers summary rows:")
    for row in brewers_summary(records):
        print(row)


if __name__ == "__main__":
    main()
