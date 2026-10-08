"""Portable data validation for Origin figures; no COM or plotting dependencies."""
from __future__ import annotations
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import re

PALETTE = ['#6699CC', '#F14040', '#666666', '#37AD6B', '#B177DE']

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def number(value, label, missing=False):
    if value is None and missing:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label}: expected a finite number' + (' or null' if missing else ''))
    return float(value)

def positive(value, label):
    result = number(value, label)
    if result <= 0:
        raise ValueError(f'{label}: expected a positive value')
    return result

def color(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9A-Fa-f]{6}', value):
        raise ValueError('Colors must use #RRGGBB')
    return value.upper()

def text(value, label):
    if not isinstance(value, str) or '\x00' in value:
        raise ValueError(f'{label}: expected text without NUL')
    return value

def axis(cfg, label):
    result = copy.deepcopy(cfg)
    lim = result.get('limits')
    if not isinstance(lim, list) or len(lim) != 2:
        raise ValueError(f'{label}.limits must have two numbers')
    result['limits'] = [number(v, label + '.limits') for v in lim]
    if lim[0] == lim[1]:
        raise ValueError(f'{label}: zero-width axis')
    result['label'] = text(result.get('label', ''), label + '.label')
    result['scale'] = result.get('scale', 'linear')
    if result['scale'] not in ('linear', 'log'):
        raise ValueError('Only linear and log axes are supported')
    if result['scale'] == 'log' and min(lim) <= 0:
        raise ValueError('Log axes require positive limits')
    result['increment'] = positive(result.get('increment', abs(lim[1] - lim[0]) / 4), label + '.increment')
    decimals = result.get('decimals', 0)
    if isinstance(decimals, bool) or not isinstance(decimals, int) or not 0 <= decimals <= 8:
        raise ValueError('decimals must be an integer from 0 to 8')
    result['decimals'] = decimals
    if 'labels' in result:
        result['labels'] = [text(v, label + '.labels') for v in result['labels']]
        if any(not v or any(c.isspace() for c in v) for v in result['labels']):
            raise ValueError('Native categorical tick labels must be nonempty single tokens')
        if result['scale'] != 'linear' or result['increment'] != 1:
            raise ValueError('Categorical ticks require a linear axis and increment 1')
    return result

def read_numeric_csv(path, columns):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('CSV requires unique column headers')
        if any(c not in reader.fieldnames for c in columns):
            raise ValueError(f'CSV columns not found: {columns}')
        values = {c: [] for c in columns}
        for row in reader:
            for c in columns:
                try:
                    value = float(row[c])
                except (ValueError, TypeError):
                    raise ValueError(f'CSV has invalid numeric value in {c}') from None
                values[c].append(number(value, c))
    if not values[columns[0]]:
        raise ValueError('CSV has no data rows')
    return values

def normalize_rows(values):
    """Normalize counts, keeping zero-observation and untested rows missing."""
    result = []
    for row in values:
        if all(v is None for v in row):
            result.append(list(row))
            continue
        if any(v is None for v in row):
            raise ValueError('Cannot row-normalize partially missing counts')
        if any(v < 0 for v in row):
            raise ValueError('Row-normalized counts must be nonnegative')
        total = sum(row)
        result.append([v / total for v in row] if total else [None] * len(row))
    return result

def resolve_series(source, base, hashes, index):
    s = copy.deepcopy(source)
    if 'csv' in s:
        csv_cfg = s.pop('csv')
        path = (base / csv_cfg['path']).resolve()
        keys = ['x', 'y'] + (['yerr'] if 'yerr' in csv_cfg else [])
        cols = [csv_cfg[k] for k in keys]
        hashes[str(path)] = sha256(path)
        data = read_numeric_csv(path, cols)
        for k, c in zip(keys, cols):
            if k in s:
                raise ValueError('Do not specify both CSV and inline values')
            s[k] = data[c]
    s['kind'] = s.get('kind', 'line')
    if s['kind'] not in ('line', 'scatter', 'errorbar', 'bar'):
        raise ValueError('Supported series: line, scatter, errorbar, bar')
    for key in ('x', 'y'):
        if not isinstance(s.get(key), list) or not s[key]:
            raise ValueError('Series requires nonempty x and y arrays')
        s[key] = [number(v, key) for v in s[key]]
    if len(s['x']) != len(s['y']):
        raise ValueError('Unequal x/y lengths')
    if s['kind'] == 'errorbar':
        if not isinstance(s.get('yerr'), list) or len(s['yerr']) != len(s['y']):
            raise ValueError('Errorbar requires matching yerr values')
        s['yerr'] = [number(v, 'yerr') for v in s['yerr']]
        if min(s['yerr']) < 0:
            raise ValueError('Error magnitudes cannot be negative')
    elif 'yerr' in s:
        raise ValueError('Use a separate errorbar series for error overlays')
    s['color'] = color(s.get('color', PALETTE[index % len(PALETTE)]))
    s['label'] = text(s.get('label', ''), 'series.label')
    s['line_width_pt'] = positive(s.get('line_width_pt', 1), 'line_width_pt')
    s['marker_size_pt'] = positive(s.get('marker_size_pt', 4), 'marker_size_pt')
    s['marker'] = s.get('marker', 'circle' if s['kind'] in ('scatter', 'errorbar') else 'none')
    if s['marker'] not in ('none', 'circle', 'square', 'triangle'):
        raise ValueError('Unknown marker')
    s['dash'] = s.get('dash', 'solid')
    if s['dash'] not in ('solid', 'dash', 'dot', 'dashdot'):
        raise ValueError('Unknown line style')
    if s['kind'] == 'bar':
        s['bar_width'] = positive(s.get('bar_width', .6), 'bar_width')
        if len(set(s['x'])) != len(s['x']) or s['x'] != sorted(s['x']):
            raise ValueError('Bar x positions must be unique and increasing')
    return s

def validate_figure(source, base, hashes):
    f = copy.deepcopy(source)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', f.get('id', '')):
        raise ValueError('Figure id must be a short portable filename')
    f['kind'] = f.get('kind', 'xy')
    if f['kind'] not in ('xy', 'heatmap'):
        raise ValueError('Figure kind must be xy or heatmap')
    page = f.get('page_inches', [4, 3] if f['kind'] == 'xy' else [5.75, 4.85])
    if not isinstance(page, list) or len(page) != 2:
        raise ValueError('page_inches must have two values')
    f['page_inches'] = [positive(v, 'page_inches') for v in page]
    f['font_family'] = text(f.get('font_family', 'Arial'), 'font_family')
    if not re.fullmatch(r'[\w -]+', f['font_family'], flags=re.UNICODE):
        raise ValueError('Invalid font family')
    f['font_size_pt'] = positive(f.get('font_size_pt', 13), 'font_size_pt')
    f['axis_width_pt'] = positive(f.get('axis_width_pt', 1), 'axis_width_pt')
    dpi = f.get('dpi', 600)
    if isinstance(dpi, bool) or not isinstance(dpi, int) or not 72 <= dpi <= 2400:
        raise ValueError('dpi must be an integer from 72 to 2400')
    f['dpi'] = dpi
    f['caption'] = text(f.get('caption', ''), 'caption')
    if 'title' in f:
        raise ValueError('Use caption or an explicit in-frame annotation instead of a top title')
    default_frame = [.18, .06, .78, .72] if f['kind'] == 'xy' else [.15, .035, .73, .87]
    f['frame'] = [number(v, 'frame') for v in f.get('frame', default_frame)]
    if len(f['frame']) != 4:
        raise ValueError('frame is [left, top, width, height] in page fractions')
    x, y, w, h = f['frame']
    if min(x, y) < 0 or min(w, h) <= 0 or x + w > 1 or y + h > 1:
        raise ValueError('Frame must fit inside the page')
    if f['kind'] == 'xy':
        if not f.get('series'):
            raise ValueError('XY figure requires series')
        f['series'] = [resolve_series(s, base, hashes, i) for i, s in enumerate(f['series'])]
        for k in ('x', 'y'):
            f[k + 'axis'] = axis(f[k + 'axis'], k + 'axis')
            if f[k + 'axis']['scale'] == 'log' and any(v <= 0 for s in f['series'] for v in s[k]):
                raise ValueError('Log plots require positive data')
    else:
        m = copy.deepcopy(f['matrix'])
        values = m.get('values')
        if not isinstance(values, list) or not values or not isinstance(values[0], list) or not values[0]:
            raise ValueError('Matrix must be nonempty and two-dimensional')
        nc = len(values[0])
        if any(not isinstance(r, list) or len(r) != nc for r in values):
            raise ValueError('Ragged matrix')
        m['original_values'] = [[number(v, 'matrix', missing=True) for v in r] for r in values]
        m['normalization'] = m.get('normalization', 'none')
        if m['normalization'] not in ('none', 'row'):
            raise ValueError('Normalization must be none or row')
        m['values'] = normalize_rows(m['original_values']) if m['normalization'] == 'row' else m['original_values']
        finite = [v for r in m['values'] for v in r if v is not None]
        if not finite:
            raise ValueError('Matrix has no observed values')
        default_limits = [0, 1] if m['normalization'] == 'row' else [min(finite), max(finite)]
        if default_limits[0] == default_limits[1]:
            default_limits[1] += 1
        m['limits'] = [number(v, 'matrix.limits') for v in m.get('limits', default_limits)]
        if len(m['limits']) != 2 or m['limits'][1] <= m['limits'][0]:
            raise ValueError('Matrix limits must be increasing')
        if min(finite) < m['limits'][0] or max(finite) > m['limits'][1]:
            raise ValueError('Matrix limits would conceal out-of-range values')
        m['low_color'] = color(m.get('low_color', '#F7FBFF'))
        m['high_color'] = color(m.get('high_color', '#08306B'))
        m['missing_color'] = color(m.get('missing_color', '#F1F1F1'))
        m['digits'] = m.get('digits', 2)
        if isinstance(m['digits'], bool) or not isinstance(m['digits'], int) or not 0 <= m['digits'] <= 8:
            raise ValueError('Matrix digits must be 0 to 8')
        m['annotate'] = m.get('annotate', True)
        if not isinstance(m['annotate'], bool):
            raise ValueError('annotate must be boolean')
        m['missing_row_label'] = text(m.get('missing_row_label', 'Not tested'), 'missing_row_label')
        m['colorbar_label'] = text(m.get('colorbar_label', 'Proportion' if m['normalization'] == 'row' else 'Value'), 'colorbar_label')
        nr = len(values)
        if 'frame' not in source:
            # Square physical cells, including non-square matrices.
            h = w * page[0] * nr / (page[1] * nc)
            if y + h > .95:
                h = .9
                w = h * page[1] * nc / (page[0] * nr)
                if x + w > .88:
                    raise ValueError('Specify page/frame dimensions suitable for this matrix')
            f['frame'] = [x, y, w, h]
        f['xaxis'] = axis(f.get('xaxis', {'label': 'Predicted class', 'limits': [.5, nc + .5], 'increment': 1}), 'xaxis')
        f['yaxis'] = axis(f.get('yaxis', {'label': 'True class', 'limits': [nr + .5, .5], 'increment': 1}), 'yaxis')
        if f['xaxis']['limits'] != [.5, nc + .5] or f['yaxis']['limits'] != [nr + .5, .5]:
            raise ValueError('Heatmap axes must preserve full cell extents and row order')
        if abs(w * page[0] / nc - h * page[1] / nr) > 1e-6:
            raise ValueError('Heatmap cells must be square; adjust frame/page dimensions')
        for k, count in [('xaxis', nc), ('yaxis', nr)]:
            if 'labels' in f[k] and len(f[k]['labels']) != count:
                raise ValueError('Heatmap tick labels must match its dimensions')
        f['matrix'] = m
    f['annotations'] = f.get('annotations', [])
    for a in f['annotations']:
        a['text'] = text(a['text'], 'annotation.text')
        for k in ('x', 'y'):
            a[k] = number(a[k], 'annotation.' + k)
            lo, hi = sorted(f[k + 'axis']['limits'])
            if not lo <= a[k] <= hi:
                raise ValueError('Annotation anchor must be inside the frame')
    if 'legend' in f:
        for k in ('x', 'y'):
            f['legend'][k] = number(f['legend'][k], 'legend.' + k)
            lo, hi = sorted(f[k + 'axis']['limits'])
            if not lo <= f['legend'][k] <= hi:
                raise ValueError('Legend anchor must be inside the frame')
    return f

def load_spec(path):
    path = Path(path).resolve(strict=True)
    def reject_constant(value):
        raise ValueError(f'Invalid JSON constant: {value}; use null for missing values')
    document = json.loads(path.read_text(encoding='utf-8-sig'), parse_constant=reject_constant)
    if document.get('schema_version') != 1 or not document.get('figures'):
        raise ValueError('Expected schema_version 1 and a nonempty figures array')
    hashes = {str(path): sha256(path)}
    figures = [validate_figure(f, path.parent, hashes) for f in document['figures']]
    if len({f['id'] for f in figures}) != len(figures):
        raise ValueError('Figure ids must be unique')
    return figures, hashes

def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def ensure_sources_unchanged(hashes):
    for p, expected in hashes.items():
        if sha256(p) != expected:
            raise RuntimeError(f'Source file changed during plotting: {p}')

def new_directory(path):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        raise FileExistsError('Use a new or empty output directory; existing results are preserved')
    return path
