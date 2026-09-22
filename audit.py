"""Validate the public source and export descriptive checks. Python 3.10+, stdlib only."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'data/SouthGermanCredit.asc'
SHA256 = '5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f'
NUMERIC = ['laufzeit', 'hoehe', 'alter']
# Ordered variables are also treated as categorical in the proposed baseline.
DOMAINS = dict(laufkont=range(1,5), moral=range(5), verw=range(11),
 sparkont=range(1,6), beszeit=range(1,6), rate=range(1,5), famges=range(1,5),
 buerge=range(1,4), wohnzeit=range(1,5), verm=range(1,5), weitkred=range(1,4),
 wohn=range(1,4), bishkred=range(1,5), beruf=range(1,5), pers=range(1,3),
 telef=range(1,3), gastarb=range(1,3), kredit=range(2))

def wilson(k, n):
    z = 1.959963984540054
    p = k/n
    center = (p + z*z/(2*n))/(1+z*z/n)
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [center-half, center+half]

def run():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SHA256:
        raise ValueError('Source differs from the reviewed UCI file')
    lines = SOURCE.read_text().splitlines()
    header = lines[0].split()
    if len(header) != 21 or len(set(header)) != 21:
        raise ValueError('Unexpected header')
    rows = []
    for number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        values = line.split()
        if len(values) != len(header):
            raise ValueError(f'Incomplete record on source line {number}')
        rows.append(dict(zip(header, map(int, values))))
    if len(rows) != 1000 or set(header) != set(NUMERIC) | set(DOMAINS):
        raise ValueError('Unexpected size or schema')
    for row in rows:
        for name, valid in DOMAINS.items():
            if row[name] not in valid:
                raise ValueError(f'Invalid category: {name}')
        if any(row[name] <= 0 for name in NUMERIC):
            raise ValueError('Nonpositive numerical value')
    out = ROOT / 'audit'
    out.mkdir(exist_ok=True)
    counts = Counter(row['kredit'] for row in rows)
    report = {
        'source_sha256': digest, 'rows': len(rows), 'columns': len(header),
        'predictors': len(header)-1, 'incomplete_records': 0,
        'invalid_category_codes': 0,
        'duplicate_rows': len(rows)-len({tuple(r[c] for c in header) for r in rows}),
        'target': {'good_kredit_1': counts[1], 'bad_kredit_0': counts[0]},
        'numeric_ranges': {c: [min(r[c] for r in rows), max(r[c] for r in rows)] for c in NUMERIC},
        'age_threshold_sensitivity': {},
        'notes': [
            'Unknown/no-account categories are valid source codes, not verified absence of missing information.',
            'Wilson intervals describe within-sample proportions; this case-control sample does not identify population default rates.',
            'No model fitted; descriptive age differences do not establish discrimination.'
        ]
    }
    for threshold in (20,25,30):
        groups = {}
        for label, select in [('below', lambda a: a<threshold), ('at_or_above', lambda a: a>=threshold)]:
            group = [r for r in rows if select(r['alter'])]
            bad = sum(r['kredit']==0 for r in group)
            groups[label] = {'n':len(group), 'bad':bad, 'good':len(group)-bad,
                             'bad_rate':bad/len(group), 'wilson_95':wilson(bad,len(group))}
        report['age_threshold_sensitivity'][str(threshold)] = groups
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    with (out/'column_summary.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['column','role','baseline_encoding','distinct','min','max'])
        for c in header:
            role = 'target_original' if c=='kredit' else 'predictor'
            encoding = 'y_bad = 1 - kredit' if c=='kredit' else ('scale for logistic regression' if c in NUMERIC else 'one-hot encoding')
            writer.writerow([c,role,encoding,len({r[c] for r in rows}),min(r[c] for r in rows),max(r[c] for r in rows)])
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    run()
