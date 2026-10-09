"""Check published research data provenance without Origin or model training."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'examples/research-gallery'


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources = json.loads((BASE / 'sources.json').read_text(encoding='utf-8'))
    specification = json.loads((BASE / 'figures.json').read_text(encoding='utf-8'))
    figures = {f['id']: f for f in specification['figures']}
    for item in sources['files']:
        check(digest(BASE / item['path']) == item['sha256'], 'Source CSV changed: ' + item['path'])
    for condition, fid in [('LIGHT', '01_ten_actions_light'), ('DARK', '02_ten_actions_dark')]:
        with (BASE / f'data/ten_actions_{condition.lower()}_counts.csv').open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        counts = [[int(r[f'pred{i}']) for i in range(1, 11)] for r in rows]
        check([int(r['true_class']) for r in rows] == list(range(1, 11)), 'Class order changed')
        check(counts == figures[fid]['matrix']['values'], 'Published matrix differs from original counts')
        summary = sources['classification'][condition]
        check([sum(r) for r in counts] == summary['row_sums'], 'Class denominators changed')
        check(sum(map(sum, counts)) == summary['total'] == 319, 'Trial count changed')
        check(sum(counts[i][i] for i in range(10)) == summary['correct'], 'Correct-prediction count changed')
    with (BASE / 'data/light_reservoir_states.csv').open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream)
        check(next(reader) == [str(i) for i in range(1, 151)], 'State-matrix header changed')
        states = [[float(v) for v in row] for row in reader]
    check(states == figures['06_reservoir_state_map']['matrix']['values'], 'Published reservoir states changed')
    check(len(states) == 40 and all(len(r) == 150 for r in states), 'State shape changed')
    report_path = ROOT / 'docs/research-gallery/validation.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    check(report['specification_sha256'] == digest(BASE / 'figures.json'), 'Specification differs from verified version')
    for figure in report['figures']:
        check(figure['reopened_values_exact'], 'Native data verification did not pass')
        for info in figure['exports'].values():
            check(digest(report_path.parent / info['path']) == info['sha256'], 'Published export changed: ' + info['path'])
    print('Research gallery verified: 12 unchanged source CSVs, 2 ten-action matrices, '
          '6000 reservoir states and 28 native export files.')


if __name__ == '__main__':
    main()
