# Rebel Stakes Deep Dive

Technologies used: Python 3 standard library (`csv`, `pathlib`) for feature engineering and scoring; markdown for reporting.

## Part A: Data Preparation & Feature Engineering
- **Turn Time** = Last_E2 − Last_E1. Example: Victory Light turn time = 23 (112−89).【F:analysis/rebel_summary.md†L3-L7】
- **Had Trouble** flag (keywords checked/steadied/blocked/wide/bumped/altered course): Crescent Moons and Royal Banner flagged due to "Steadied...blocked" and "Wide trip" comments.【F:analysis/rebel_summary.md†L5-L9】
- **Fitness Flag** (third off layoff pattern) = 0 for all runners; none returned from >45-day break with improving figures.【F:analysis/rebel_summary.md†L3-L9】

## Part B: Quantitative Modeling & Fair Odds
Features used and justification:
1. **Prime Power (25%)** – holistic Brisnet composite capturing class/speed/form.
2. **Last Speed (20%)** – most recent performance level.
3. **Last LP (15%)** – finishing energy, key in projected tiring pace.
4. **Turn Time (15%)** – acceleration on far turn, predictive of stretch run.
5. **Class Rating (15%)** – quality of competition faced.
6. **Had Trouble (−5% penalty)** – downgrade compromised last trips.
7. **Fitness Flag (+5% bonus)** – reward improving 3rd-off-layoff pattern (none here).

Performance Scores were normalized and combined per the weights above.【F:analysis/rebel_analysis.py†L34-L79】 Model probabilities and fair odds:

| Horse | Model Prob | Fair Odds (decimal) | ML Decimal | Overlay? |
| --- | --- | --- | --- | --- |
| Storm Seeker | 0.226 | 4.43 | 11.00 | Underlay |
| Victory Light | 0.205 | 4.88 | 3.50 | **Overlay** |
| Crescent Moons | 0.191 | 5.23 | 7.00 | Underlay |
| Silver Verdict | 0.106 | 9.44 | 5.00 | **Overlay** |
| Odyssey King | 0.088 | 11.37 | 16.00 | Underlay |
| Midnight Shadow | 0.085 | 11.81 | 9.00 | **Overlay** |
| Ridge Runner | 0.077 | 12.91 | 13.00 | Underlay |
| Royal Banner | 0.022 | 44.97 | 21.00 | **Overlay** |

(Overlay defined per instructions: Fair Odds > Market Odds.)【F:analysis/rebel_summary.md†L3-L9】

## Part C: Qualitative Synthesis & Wagering
### C1. Bias & Race Shape Adjustments
- **Upgrade:** Crescent Moons (S; strong late pace 110 and turn-time +7; fits closer bias), Royal Banner (S; wide trip last time, benefits from tiring speed), Odyssey King (S; late kick 104), all suited to dead rail/closer-friendly pattern.【F:analysis/rebel_summary.md†L5-L9】
- **Downgrade:** Storm Seeker and Midnight Shadow (pure E; projected hot pace, bias against front speed), Silver Verdict/Victory Light (E/P; tactical but could get cooked if duel), favoring stalk-and-pounce trips.【F:analysis/rebel_summary.md†L3-L7】

### C2. Final Win Bets
1. **Victory Light** – Model #2 with 20.5% win chance, fair 4.88 vs 3.50 ML (overlay); tactical E/P can sit behind dueling E types and avoid dead rail; strong turn time 23 and balanced figures.【F:analysis/rebel_summary.md†L3-L5】
2. **Royal Banner** – Longshot S closer with wide-trip trouble flag; fair 44.97 vs 21.00 ML (major overlay); closing style and outside draw ideal for closer bias and collapsing pace.【F:analysis/rebel_summary.md†L8-L9】

### C3. Exacta Ticket ($100 Budget)
Key Victory Light on top (expected best blend of form/value) over bias-favored closers.
- $20 Exacta: Victory Light → Crescent Moons
- $20 Exacta: Victory Light → Silver Verdict
- $20 Exacta: Victory Light → Odyssey King
- $20 Exacta: Victory Light → Royal Banner
- $10 Saver: Crescent Moons → Victory Light
- $10 Saver: Silver Verdict → Victory Light

**Total = $100.** This keys the top value pick over four logical closers (pace/bias advantage) with small reverse savers to capture a closer-first outcome.
