# Rebel Stakes Deep Dive

Technologies used: Python 3 standard library (`csv`, `dataclasses`, `pathlib`).

## Part A: Data Preparation & Feature Engineering
- **Turn Time** = Last_E2 − Last_E1. Calculated per runner.
- **Had Trouble** flag (keywords checked/steadied/blocked/wide/bumped/altered course).
- **Fitness Flag** (third off layoff pattern) = Days_Off > 45 and Last_Speed > Avg_Speed_Last_3 (none qualify in this dataset).

## Part B: Quantitative Modeling & Fair Odds
Features and weights: {'prime_power': 0.25, 'last_speed': 0.2, 'last_lp': 0.15, 'turn_time': 0.15, 'class_rating': 0.15, 'fitness_flag': 0.05, 'had_trouble': -0.05}.
Model probabilities and fair odds:

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

## Part C: Qualitative Synthesis & Wagering
- **Upgrade (closer bias + hot pace):** Crescent Moons, Royal Banner, Odyssey King.
- **Downgrade (dead rail/early fade risk):** Midnight Shadow, Storm Seeker.

Win bets: Victory Light and Silver Verdict chosen from overlay + bias-adjusted ranks.

Exacta strategy (scaled to $100):
- $18.18 Exacta: Victory Light → Crescent Moons
- $18.18 Exacta: Victory Light → Royal Banner
- $18.18 Exacta: Victory Light → Odyssey King
- $9.09 Exacta saver: Crescent Moons → Victory Light
- $9.09 Exacta saver: Royal Banner → Victory Light
- $9.09 Exacta saver: Odyssey King → Victory Light
- $18.18 Exacta: Victory Light → Silver Verdict (confidence companion)
Total allocated: $100.00
