import csv
from pathlib import Path

raw = []
with open(Path(__file__).resolve().parent.parent / 'rebel_stakes_data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # convert numeric fields
        for fld in ['PP', 'Days_Off', 'Avg_Speed_Last_3', 'Last_Speed', 'Career_Top', 'Last_E1', 'Last_E2', 'Last_LP', 'Prime_Power', 'Class_Rating']:
            if row[fld] != '':
                row[fld] = float(row[fld]) if '.' in row[fld] else int(row[fld])
            else:
                row[fld] = 0
        raw.append(row)

# Feature engineering
for row in raw:
    row['Turn_Time'] = row['Last_E2'] - row['Last_E1']
    comment = (row['Last_Race_Comment'] or '').lower()
    trouble_keywords = ['checked', 'steadied', 'blocked', 'wide', 'bumped', 'altered course']
    row['Had_Trouble'] = int(any(k in comment for k in trouble_keywords))
    row['Fitness_Flag'] = int(row['Days_Off'] > 45 and row['Last_Speed'] > row['Avg_Speed_Last_3'])

# Helper for normalization
def normalize(rows, key):
    values = [r[key] for r in rows]
    min_v, max_v = min(values), max(values)
    if max_v == min_v:
        return {i: 0.5 for i in range(len(rows))}
    return {i: (rows[i][key] - min_v) / (max_v - min_v) for i in range(len(rows))}

features = ['Prime_Power', 'Last_Speed', 'Last_LP', 'Turn_Time', 'Class_Rating']
feature_norms = {feat: normalize(raw, feat) for feat in features}

scores = []
for idx, row in enumerate(raw):
    score = (
        0.25 * feature_norms['Prime_Power'][idx]
        + 0.20 * feature_norms['Last_Speed'][idx]
        + 0.15 * feature_norms['Last_LP'][idx]
        + 0.15 * feature_norms['Turn_Time'][idx]
        + 0.15 * feature_norms['Class_Rating'][idx]
        + 0.05 * row['Fitness_Flag']
        - 0.05 * row['Had_Trouble']
    )
    scores.append(score)
    row['Performance_Score'] = score

score_sum = sum(scores)
for row in raw:
    row['Model_Prob'] = row['Performance_Score'] / score_sum if score_sum else 0
    row['Fair_Decimal_Odds'] = 1 / row['Model_Prob'] if row['Model_Prob'] else 0

# Convert ML odds

def ml_to_decimal(ml):
    try:
        top, bottom = ml.split('-')
        return 1 + float(top) / float(bottom)
    except Exception:
        return 0

for row in raw:
    row['ML_Decimal_Odds'] = ml_to_decimal(row['ML_Odds'])
    row['Overlay_Status'] = 'Overlay' if row['Fair_Decimal_Odds'] > row['ML_Decimal_Odds'] else 'Underlay'

# Output markdown summary
headers = [
    'Horse_Name', 'PP', 'ML_Odds', 'Run_Style', 'Avg_Speed_Last_3', 'Last_Speed',
    'Career_Top', 'Last_Race_Comment', 'Last_E1', 'Last_E2', 'Last_LP', 'Turn_Time',
    'Had_Trouble', 'Fitness_Flag', 'Prime_Power', 'Class_Rating', 'Performance_Score',
    'Model_Prob', 'Fair_Decimal_Odds', 'ML_Decimal_Odds', 'Overlay_Status'
]

lines = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
for row in sorted(raw, key=lambda r: r['Model_Prob'], reverse=True):
    vals = [
        row['Horse_Name'], str(row['PP']), row['ML_Odds'], row['Run_Style'],
        f"{row['Avg_Speed_Last_3']:.0f}", f"{row['Last_Speed']:.0f}", f"{row['Career_Top']:.0f}",
        row['Last_Race_Comment'], f"{row['Last_E1']:.0f}", f"{row['Last_E2']:.0f}", f"{row['Last_LP']:.0f}",
        f"{row['Turn_Time']:.0f}", str(row['Had_Trouble']), str(row['Fitness_Flag']),
        f"{row['Prime_Power']:.1f}", f"{row['Class_Rating']:.0f}", f"{row['Performance_Score']:.3f}",
        f"{row['Model_Prob']:.3f}", f"{row['Fair_Decimal_Odds']:.2f}", f"{row['ML_Decimal_Odds']:.2f}", row['Overlay_Status']
    ]
    lines.append('| ' + ' | '.join(vals) + ' |')

summary_path = Path(__file__).resolve().parent / 'rebel_summary.md'
summary_path.write_text('\n'.join(lines))
