"""Native Origin plotting with frozen data, reopened-project checks and exports."""
from __future__ import annotations
import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
import sys
import uuid

from plot_spec import load_spec, ensure_sources_unchanged, new_directory, sha256, write_json

MISSING = -1.23456789e-300

def n(value):
    return format(float(value), '.16g')

def rgb(value):
    return 'color(' + ','.join(str(int(value[i:i + 2], 16)) for i in (1, 3, 5)) + ')'

def blend(low, high, fraction):
    a = [int(low[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(high[i:i + 2], 16) for i in (1, 3, 5)]
    return 'color(' + ','.join(str(round(x + fraction * (y - x))) for x, y in zip(a, b)) + ')'

def cell_label(value, digits):
    if value is None:
        return ''
    return str(int(value)) if value in (0, 1) else f'{value:.{digits}f}'

def colorbar_tick_decimals(low, high):
    """Keep fractional colorbar steps distinct, including ranges wider than one."""
    increment = (high - low) / 5
    ticks = [low + i * increment for i in range(6)]
    minimum = 1 if high - low <= 1 else 0
    for digits in range(minimum, 9):
        if all(math.isclose(round(v, digits), v, rel_tol=0,
                            abs_tol=abs(increment) * 1e-9) for v in ticks):
            return digits
    return 8

def doctor():
    result = {'windows': sys.platform == 'win32', 'python': sys.version.split()[0],
              'modules': {k: importlib.util.find_spec(k) is not None for k in ['numpy', 'win32com', 'PIL', 'pymupdf']},
              'origin_com_available': False}
    if result['windows'] and result['modules']['win32com']:
        import win32com.client
        app = None
        try:
            app = win32com.client.DispatchEx('Origin.Application')
            app.Visible = 0
            result.update(origin_com_available=True, origin_internal_version=app.Evaluate('system.version'))
        except Exception as e:
            result['origin_error'] = str(e)
        finally:
            if app is not None:
                app.Exit()
    return result

class OriginSession:
    def __init__(self):
        if sys.platform != 'win32':
            raise RuntimeError('Native Origin automation requires Windows')
        import numpy as np
        import pythoncom
        import win32com.client
        self.np = np
        self.pythoncom = pythoncom
        self.win32com = win32com.client
        self.app = win32com.client.DispatchEx('Origin.Application')
        self.app.Visible = 0
        self.log = []
        self.data = []
        self.text_names = []
        self.layer_frames = {}

    def close(self):
        self.app.Exit()

    def lt(self, command):
        ok = bool(self.app.Execute(command))
        self.log.append({'command': command, 'ok': ok})
        if not ok:
            raise RuntimeError('Origin rejected a command: ' + command)

    def ev(self, expression):
        return float(self.app.Evaluate(expression))

    def string(self, variable, value):
        # COM string assignment preserves quotes and Unicode without embedding
        # user text into executable LabTalk code.
        self.app.SetLTStr(variable, str(value))
        got = self.app.GetLTStr(variable)
        if got != str(value):
            raise RuntimeError('Origin string round-trip failed: ' + variable)

    def active(self, layer):
        self.lt(f'win -a Figure; page.active={layer};')

    def style_axes(self, figure, layer, frame, xcfg, ycfg, colorbar=False):
        self.active(layer)
        self.layer_frames[layer] = list(frame)
        left, top, width, height = frame
        self.lt(f'layer.fixed=1; layer.factor=1; layer.unit=1; layer.left={n(left * 100)}; '
                f'layer.top={n(top * 100)}; layer.width={n(width * 100)}; layer.height={n(height * 100)}; '
                'layer.factor=1; layer.maxpts=0; layer.matmaxptsenabled=0;')
        family = figure['font_family']
        fs = figure['font_size_pt']
        aw = figure['axis_width_pt']
        self.lt('layer.x.showAxes=3; layer.y.showAxes=3; layer.x.showGrids=0; layer.y.showGrids=0; '
                'label -r Legend; label -r XB; label -r YL; label -r XT; label -r YR;')
        for side in ('x', 'x2', 'y', 'y2'):
            self.lt(f'layer.{side}.thickness={n(aw)}; layer.{side}.color=1; '
                    f'layer.{side}.label.font=font("{family}"); layer.{side}.label.pt={n(fs)}; '
                    f'layer.{side}.label.bold=0; layer.{side}.minorTicks=0; layer.{side}.ticks=0;')
        self.lt('layer.tickW=1; layer.tickL=5;')
        for k, cfg in [('x', xcfg), ('y', ycfg)]:
            lo, hi = cfg['limits']
            inc = cfg['increment'] * (1 if hi > lo else -1)
            self.lt(f'layer.{k}.type={2 if cfg["scale"] == "log" else 1}; '
                    f'layer.{k}.from={n(lo)}; layer.{k}.to={n(hi)}; layer.{k}.rescale=0; '
                    f'layer.{k}.majorTicks=0; layer.{k}.inc={n(inc)}; layer.{k}.showLabels=1; '
                    f'layer.{k}.label.type=1; layer.{k}.label.numFormat={2 if cfg["scale"] == "log" else 1}; '
                    f'layer.{k}.label.decPlaces={cfg["decimals"]}; layer.{k}.label.rotate=0;')
            if cfg.get('labels'):
                self.string('OSPTicks$', ' '.join(cfg['labels']))
                self.lt(f'layer.{k}.label.type=10; layer.{k}.label.string$=OSPTicks$;')
        if colorbar:
            self.lt('layer.x.showAxes=0; layer.x.showLabels=0; layer.x2.showLabels=0; '
                    'layer.y.showLabels=2; layer.y.showlabel=0; layer.y2.showlabel=1; '
                    'layer.y2.label.type=1; layer.y2.label.numFormat=1; '
                    f'layer.y2.label.decPlaces={ycfg["decimals"]};')
        else:
            self.lt(f'layer.x.ticks={0 if figure["kind"] == "heatmap" else 1}; '
                    f'layer.y.ticks={0 if figure["kind"] == "heatmap" else 1};')
            for role, name, command, cfg in [('x', 'XB', 'xb', xcfg), ('y', 'YL', 'yl', ycfg)]:
                self.lt(f'label -{command} "placeholder";')
                self.string('OSPText$', cfg['label'])
                self.lt(f'{name}.text$=OSPText$; {name}.font=font("{family}"); {name}.fsize={n(fs)};')
            # Explicit native positions avoid accumulating title space above
            # the page and keep labels stable during native page compaction.
            xa, xb = xcfg['limits']; ya, yb = ycfg['limits']
            xmid = math.sqrt(xa * xb) if xcfg['scale'] == 'log' else (xa + xb) / 2
            ymid = math.sqrt(ya * yb) if ycfg['scale'] == 'log' else (ya + yb) / 2
            ytitle = ya * (ya / yb) ** .16 if ycfg['scale'] == 'log' else ya - .16 * (yb - ya)
            xtitle = xa * (xa / xb) ** .16 if xcfg['scale'] == 'log' else xa - .16 * (xb - xa)
            self.lt(f'XB.x={n(xmid)}; XB.y={n(ytitle)}; YL.x={n(xtitle)}; YL.y={n(ymid)}; YL.rotate=90;')

    def label(self, figure, layer, name, value, x, y, fill='#000000', rotate=0):
        self.active(layer)
        self.lt(f'label -p 0 0 -j 1 -sa -n {name} "placeholder";')
        self.string('OSPText$', value)
        self.lt(f'{name}.text$=OSPText$; {name}.font=font("{figure["font_family"]}"); '
                f'{name}.fsize={n(figure["font_size_pt"])}; {name}.color={rgb(fill)}; '
                f'{name}.rotate={rotate}; {name}.attach=2; {name}.x={n(x)}; {name}.y={n(y)};')
        self.text_names.append((layer, name, value))

    def worksheet(self, values, headers):
        name = f'Data{1 + sum(d["kind"] == "worksheet" for d in self.data):03d}'
        array = self.np.asarray(values, dtype=float)
        self.lt(f'newbook name:={name} option:=lsname; wks.ncols={array.shape[1]}; wks.nrows={array.shape[0]};')
        for i, title in enumerate(headers, 1):
            self.string('OSPText$', title)
            self.lt(f'wks.col{i}.type={4 if i == 1 else 3 if i == 3 else 1}; wks.col{i}.lname$=OSPText$;')
        variant = self.win32com.VARIANT(self.pythoncom.VT_ARRAY | self.pythoncom.VT_R8, tuple(map(tuple, array)))
        if not self.app.PutWorksheet(f'[{name}]1!', variant, 0, 0):
            raise RuntimeError('PutWorksheet failed')
        self.data.append({'kind': 'worksheet', 'name': name, 'values': array.tolist(), 'headers': headers})
        return name

    def curve(self, figure, series):
        kind = series['kind']
        rows = list(zip(series['x'], series['y'], series['yerr'])) if kind == 'errorbar' else list(zip(series['x'], series['y']))
        name = self.worksheet(rows, ['X', series['label'] or 'Y'] + (['Y error'] if kind == 'errorbar' else []))
        self.active(1)
        marker = {'none': 0, 'circle': 2, 'square': 1, 'triangle': 3}[series['marker']]
        code = 203 if kind == 'bar' else 201 if kind == 'scatter' else 202 if marker or kind == 'errorbar' else 200
        self.lt(f'plotxy iy:=[{name}]1!({"1,2,3" if kind == "errorbar" else "1,2"}) plot:={code} ogl:=[Figure]1!; '
                f'range rp=[{name}]1!col(2);')
        dash_code = {'solid': 0, 'dash': 1, 'dot': 2, 'dashdot': 3}[series['dash']]
        self.lt(f'set rp -c {rgb(series["color"])}; set rp -wp {n(series["line_width_pt"])}; '
                f'set rp -d {dash_code};')
        if kind == 'bar':
            interval = min(self.np.diff(series['x'])) if len(series['x']) > 1 else 1
            gap = 100 * (1 - series['bar_width'] / interval)
            self.lt(f'set rp -cf {rgb(series["color"])}; set rp -vg {n(gap)};')
        else:
            self.lt(f'set rp -l {0 if kind == "scatter" else 1}; '
                    f'set rp -k {marker or (2 if kind in ("scatter", "errorbar") else 0)}; '
                    f'set rp -z {n(series["marker_size_pt"])}; set rp -kf 0;')
        if kind == 'errorbar':
            self.lt(f'range er=[{name}]1!col(3); set er -c {rgb(series["color"])}; '
                    f'set er -wp {n(series["line_width_pt"])}; set er -z 6;')

    def matrix(self, figure, layer, values, low, high, coordinates, auxiliary=False):
        name = f'Matrix{1 + sum(d["kind"] == "matrix" for d in self.data):02d}'
        array = self.np.asarray([[MISSING if v is None else v for v in r] for r in values], dtype=float)
        nr, nc = array.shape
        x1, x2, y1, y2 = coordinates
        self.lt(f'newbook name:={name} mat:=1 option:=lsname; wks.nrows={nr}; wks.ncols={nc}; '
                f'wks.col1.x1={n(x1)}; wks.col1.x2={n(x2)}; wks.col1.y1={n(y1)}; wks.col1.y2={n(y2)};')
        variant = self.win32com.VARIANT(self.pythoncom.VT_ARRAY | self.pythoncom.VT_R8, tuple(map(tuple, array)))
        if not self.app.PutMatrix(name, variant):
            raise RuntimeError('PutMatrix failed')
        self.data.append({'kind': 'matrix', 'name': name, 'values': values, 'auxiliary_colorbar': auxiliary})
        self.active(layer)
        self.lt(f'plotm im:=[{name}]1!1 plot:=105 ogl:=[Figure]{layer}!; '
                f'layer.cmap.zmin={n(low)}; layer.cmap.zmax={n(high)}; '
                'layer.cmap.numMajorLevels=8; layer.cmap.numMinorLevels=31; layer.cmap.SetLevels(1);')
        matrix = figure['matrix']
        count = int(self.ev('layer.cmap.numColors'))
        commands = [f'layer.cmap.color{i}={blend(matrix["low_color"], matrix["high_color"], (i - 1) / (count - 1))};' for i in range(1, count + 1)]
        for i in range(0, len(commands), 20):
            self.lt(' '.join(commands[i:i + 20]))
        self.lt(f'layer.cmap.colorBelow={rgb(matrix["low_color"])}; layer.cmap.colorAbove={rgb(matrix["high_color"])}; '
                f'layer.cmap.colorMiss={rgb(matrix["missing_color"])}; layer.cmap.updateScale();')

    def redraw(self):
        # Some Origin versions do not redraw native title positions while hidden.
        self.app.Visible = 1
        self.lt('doc -uw; sec -p 0.2;')
        # Origin 2021 can initialize a new matrix layer's label visibility
        # when the graph is first shown. Restore the intended sides afterward.
        for layer in self.layer_frames:
            self.active(layer)
            if layer == 2 and self.figure['kind'] == 'heatmap':
                self.lt('layer.x.showLabels=0;layer.y.showLabels=2; '
                        'layer.x.showlabel=0;layer.x2.showlabel=0; '
                        'layer.y.showlabel=0;layer.y2.showlabel=1;')
            else:
                self.lt('layer.x.showLabels=1;layer.y.showLabels=1; '
                        'layer.x.showlabel=1;layer.x2.showlabel=0; '
                        'layer.y.showlabel=1;layer.y2.showlabel=0;')
        self.active(1)
        self.lt('doc -uw; sec -p 0.2;')
        self.app.Visible = 0

    def pad_page(self, figure):
        # Leave temporary physical room for axis titles before measuring a
        # tight page. Cropping an already clipped preview cannot recover text.
        pad = .12 + 2 * figure['font_size_pt'] / 72
        old_w, old_h = self.ev('page.width/page.resx'), self.ev('page.height/page.resy')
        new_w, new_h = old_w + 2 * pad, old_h + 2 * pad
        frames = {i: [(f[0] * old_w + pad) / new_w, (f[1] * old_h + pad) / new_h,
                      f[2] * old_w / new_w, f[3] * old_h / new_h] for i, f in self.layer_frames.items()}
        self.lt(f'page.width={n(new_w)}*page.resx;page.height={n(new_h)}*page.resy;')
        for i, frame in frames.items():
            self.active(i)
            self.lt('layer.factor=1;layer.unit=1; ' + ' '.join(f'layer.{key}={n(value*100)};' for key,value in zip(['left','top','width','height'],frame)))
        self.layer_frames = frames

    def export(self, figure, directory, extension):
        self.active(1)
        self.string('OSPExportPath$', str(directory))
        self.string('OSPStem$', figure['id'])
        extra = f'tr2.PNG.dotsperinch:={figure["dpi"]}' if extension == 'png' else 'tr2.PDF.Fonts.Embed:=1' if extension == 'pdf' else ''
        self.lt(f'expGraph type:={extension} filename:=OSPStem$ path:=OSPExportPath$ overwrite:=replace '
                f'tr.margin:=2 tr.SpeedMode:=2 tr1.unit:=0 tr1.width:={n(self.ev("page.width/page.resx"))} {extra};')
        path = directory / f'{figure["id"]}.{extension}'
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError('Origin did not create the expected export: ' + str(path))
        return path

    def compact_page(self, figure, directory):
        """Crop native page/layers together; never crop only a rendered bitmap."""
        from PIL import Image, ImageChops
        png = self.export(figure, directory, 'png')
        with Image.open(png) as image:
            image = image.convert('RGB')
            difference = ImageChops.difference(image, Image.new('RGB', image.size, 'white'))
            bbox = difference.convert('L').point(lambda v: 255 if v > 12 else 0).getbbox()
            if bbox is None:
                raise RuntimeError('Origin exported a blank graph')
            pw, ph = image.size
        margin = max(6, round(figure['dpi'] * .06))
        left, top = max(0, bbox[0] - margin), max(0, bbox[1] - margin)
        right, bottom = min(pw, bbox[2] + margin), min(ph, bbox[3] + margin)
        old_w, old_h = self.ev('page.width/page.resx'), self.ev('page.height/page.resy')
        new_w, new_h = old_w * (right - left) / pw, old_h * (bottom - top) / ph
        # Preserve physical frame dimensions and positions relative to content.
        frames = {i: [(f[0] * pw - left) / (right - left), (f[1] * ph - top) / (bottom - top),
                      f[2] * pw / (right - left), f[3] * ph / (bottom - top)] for i, f in self.layer_frames.items()}
        self.lt(f'page.width={n(new_w)}*page.resx; page.height={n(new_h)}*page.resy;')
        for i, frame in frames.items():
            self.active(i)
            self.lt('layer.factor=1; layer.unit=1; ' + ' '.join(f'layer.{key}={n(value * 100)};' for key, value in zip(['left', 'top', 'width', 'height'], frame)))
        self.layer_frames = frames
        self.active(1)
        self.redraw()
        return {'page_before_inches': [old_w, old_h], 'page_after_inches': [new_w, new_h],
                'crop_bbox_pixels': [left, top, right, bottom], 'font_sizes_preserved': True,
                'physical_frame_tolerance_inches': .0025}

    def verify_native(self, figure):
        for item in self.data:
            expected = self.np.asarray([[MISSING if v is None else v for v in r] for r in item['values']], dtype=float)
            if item['kind'] == 'matrix':
                got = self.np.asarray(self.app.GetMatrix(item['name']), dtype=float)
            else:
                got = self.np.asarray(self.app.GetWorksheet(item['name'], 0, 0, expected.shape[0] - 1, expected.shape[1] - 1), dtype=float)
            if not self.np.array_equal(expected, got):
                raise RuntimeError('Reopened native values differ: ' + item['name'])
        layers = []
        page_w, page_h = self.ev('page.width/page.resx'), self.ev('page.height/page.resy')
        for i in range(1, int(self.ev('page.nlayers')) + 1):
            self.active(i)
            if self.ev('layer.factor') != 1:
                raise RuntimeError('Origin layer font scaling is not 1')
            for side in ['x', 'x2', 'y', 'y2']:
                if self.ev(f'layer.{side}.label.pt') != figure['font_size_pt'] or self.ev(f'layer.{side}.label.font==font("{figure["font_family"]}")') != 1:
                    raise RuntimeError('Native axis font mismatch')
                if abs(self.ev(f'layer.{side}.thickness') - figure['axis_width_pt']) > 1e-9:
                    raise RuntimeError('Native axis frame width mismatch')
            frame = [self.ev('layer.' + k) / 100 for k in ['left', 'top', 'width', 'height']]
            sides = [int(self.ev('layer.' + s + '.showlabel')) for s in ['x', 'x2', 'y', 'y2']]
            expected_sides = [0, 0, 0, 1] if i == 2 and figure['kind'] == 'heatmap' else [1, 0, 1, 0]
            if sides != expected_sides:
                raise RuntimeError('Native axis label sides differ')
            scales = {}
            for k in ['x', 'y']:
                cfg = figure[k + 'axis'] if i == 1 else {'limits': [0, 1] if k == 'x' else figure['matrix']['limits']}
                actual = [self.ev('layer.' + k + '.' + name) for name in ['from', 'to']]
                if not self.np.allclose(actual, cfg['limits'], rtol=1e-12, atol=1e-12):
                    raise RuntimeError('Native axis range differs: ' + k)
                scales[k] = actual
                if i == 1:
                    increment = cfg['increment'] * (1 if actual[1] > actual[0] else -1)
                    if not math.isclose(self.ev('layer.' + k + '.inc'), increment, abs_tol=1e-12):
                        raise RuntimeError('Native tick increment differs: ' + k)
            if i == 1:
                for name, cfg in [('XB', figure['xaxis']), ('YL', figure['yaxis'])]:
                    if self.ev(name + '.fsize') != figure['font_size_pt'] or self.app.GetLTStr(name + '.text$') != cfg['label']:
                        raise RuntimeError('Native axis title mismatch: ' + name)
                physical = [frame[2] * page_w, frame[3] * page_h]
                expected_physical = [figure['frame'][2] * figure['page_inches'][0], figure['frame'][3] * figure['page_inches'][1]]
                # Origin 2021 quantizes page/layer dimensions at native screen
                # resolution. This permits <0.18 pt of physical rounding.
                if not self.np.allclose(physical, expected_physical, rtol=0, atol=.0025):
                    raise RuntimeError('Physical data frame size changed during page compaction')
            layers.append({'layer': i, 'frame': frame, 'font_pt': figure['font_size_pt'],
                           'axis_ranges': scales, 'visible_label_sides': sides})
        for layer, name, expected in self.text_names:
            self.active(layer)
            if self.ev(name + '.fsize') != figure['font_size_pt'] or self.app.GetLTStr(name + '.text$') != expected:
                raise RuntimeError('Native editable label mismatch: ' + name)
        self.active(1)
        if figure['kind'] == 'heatmap' and self.ev('layer.cmap.colorMiss==' + rgb(figure['matrix']['missing_color'])) != 1:
            raise RuntimeError('Native missing-data color mismatch')
        return layers

    def build(self, figure, directory, formats):
        self.figure = figure
        self.data = []
        self.text_names = []
        self.layer_frames = {}
        if not self.app.NewProject():
            raise RuntimeError('Could not create an isolated Origin project')
        self.lt('newpanel col:=1 row:=1; win -r %H Figure;')
        w, h = figure['page_inches']
        self.lt(f'page.width={n(w)}*page.resx; page.height={n(h)}*page.resy; page.cntrl={int(self.ev("page.cntrl")) & ~512};')
        if figure['kind'] == 'heatmap':
            self.lt('layer -n;')
        self.style_axes(figure, 1, figure['frame'], figure['xaxis'], figure['yaxis'])
        if figure['kind'] == 'xy':
            for s in figure['series']:
                self.curve(figure, s)
            # plotxy can apply a template that resets axes and adds a legend.
            self.style_axes(figure, 1, figure['frame'], figure['xaxis'], figure['yaxis'])
            if 'legend' in figure:
                self.active(1)
                self.lt('legend -r;')
                entries = []
                index = 1
                for s in figure['series']:
                    if s['label']:
                        entries.append('\\l(' + str(index) + ') ' + s['label'])
                    index += 2 if s['kind'] == 'errorbar' else 1
                self.string('OSPText$', '\r\n'.join(entries))
                self.lt(f'Legend.text$=OSPText$; Legend.font=font("{figure["font_family"]}"); '
                        f'Legend.fsize={n(figure["font_size_pt"])}; Legend.background=0; '
                        f'Legend.x={n(figure["legend"]["x"])}; Legend.y={n(figure["legend"]["y"])};')
                self.text_names.append((1, 'Legend', '\r\n'.join(entries)))
        else:
            m = figure['matrix']; nr, nc = len(m['values']), len(m['values'][0]); lo, hi = m['limits']
            self.matrix(figure, 1, m['values'], lo, hi, [1, nc, 1, nr])
            self.style_axes(figure, 1, figure['frame'], figure['xaxis'], figure['yaxis'])
            for i, row in enumerate(m['values'], 1):
                if all(v is None for v in row):
                    self.label(figure, 1, f'MissingRow{i}', m['missing_row_label'], (nc + 1) / 2, i, '#666666')
                elif m['annotate']:
                    for j, value in enumerate(row, 1):
                        if value is not None:
                            self.label(figure, 1, f'Cell{i}_{j}', cell_label(value, m['digits']), j, i,
                                       '#FFFFFF' if value > lo + .55 * (hi - lo) else '#000000')
            left, top, width, height = figure['frame']
            cframe = [left + width + .025, top, .018, height]
            if cframe[0] + cframe[2] > .95:
                raise ValueError('Leave room for the colorbar and its labels')
            xcfg = {'limits': [0, 1], 'label': '', 'scale': 'linear', 'increment': 1, 'decimals': 0}
            ycfg = {'limits': [lo, hi], 'label': '', 'scale': 'linear', 'increment': (hi - lo) / 5,
                    'decimals': colorbar_tick_decimals(lo, hi)}
            self.style_axes(figure, 2, cframe, xcfg, ycfg, colorbar=True)
            vals = [[lo + (hi - lo) * i / 255] * 2 for i in range(256)]
            self.matrix(figure, 2, vals, lo, hi, [.25, .75, lo, hi], auxiliary=True)
            self.style_axes(figure, 2, cframe, xcfg, ycfg, colorbar=True)
            max_chars = max(len(f'{v:.{ycfg["decimals"]}f}') for v in [lo, hi])
            title_x = 1 + (max_chars * .6 + 1.4) * figure['font_size_pt'] / (72 * cframe[2] * w)
            self.label(figure, 2, 'ColorbarTitle', m['colorbar_label'], title_x, (lo + hi) / 2, rotate=90)
        for i, a in enumerate(figure['annotations'], 1):
            self.label(figure, 1, f'Annotation{i}', a['text'], a['x'], a['y'])
        self.active(1)
        self.pad_page(figure)
        self.redraw()
        compact = self.compact_page(figure, directory)
        temporary = directory / ('_saving_' + uuid.uuid4().hex + '.opju')
        project = directory / (figure['id'] + '.opju')
        if not self.app.Save(str(temporary)):
            raise RuntimeError('Origin project save failed')
        if not self.app.NewProject():
            raise RuntimeError('Could not release saved project')
        temporary.replace(project)
        if not self.app.Load(str(project), True):
            raise RuntimeError('Saved project could not be reopened')
        self.active(1)
        layers = self.verify_native(figure)
        files = {'opju': project.name}
        for ext in dict.fromkeys(['png'] + [v for v in formats if v != 'svg'] + (['pdf'] if 'svg' in formats else [])):
            files[ext] = self.export(figure, directory, ext).name
        qa = verify_exports(directory, figure, files)
        if 'svg' in formats:
            import pymupdf
            with pymupdf.open(directory / files['pdf']) as document:
                svg = directory / (figure['id'] + '.svg')
                svg.write_text(document[0].get_svg_image(text_as_path=True), encoding='utf-8')
            files['svg'] = svg.name
        for item in self.data:
            path = directory / (item['name'] + '.csv')
            with path.open('w', encoding='utf-8-sig', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(item.get('headers', list(range(1, len(item['values'][0]) + 1))))
                writer.writerows([['' if v is None else v for v in row] for row in item['values']])
            item['csv'] = path.name
        if figure['kind'] == 'heatmap':
            with (directory / 'original_matrix.csv').open('w', encoding='utf-8-sig', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(range(1, len(figure['matrix']['original_values'][0]) + 1))
                writer.writerows([['' if v is None else v for v in row] for row in figure['matrix']['original_values']])
        report = {'id': figure['id'], 'caption': figure['caption'], 'graph_page': 'Figure',
                  'native_origin': True, 'origin_internal_version': self.ev('system.version'),
                  'reopened_values_exact': True, 'native_layers': layers, 'native_text_objects': len(self.text_names),
                  'compact_page': compact, 'files': files, 'tables': self.data, 'export_qa': qa,
                  'svg_source': 'Converted from Origin native vector PDF; font glyphs are paths' if 'svg' in files else None,
                  'sha256': {k: sha256(directory / value) for k, value in files.items()}}
        write_json(directory / 'frozen_spec.json', figure)
        write_json(directory / 'verification.json', report)
        return report

def verify_exports(directory, figure, files):
    from PIL import Image, ImageChops
    with Image.open(directory / files['png']) as image:
        image = image.convert('RGB')
        w, h = image.size
        bbox = ImageChops.difference(image, Image.new('RGB', image.size, 'white')).convert('L').point(lambda v: 255 if v > 12 else 0).getbbox()
        if bbox is None:
            raise RuntimeError('Blank final preview')
        margins = [bbox[0], bbox[1], w - bbox[2], h - bbox[3]]
        if min(margins) < 3:
            raise RuntimeError('Content touches page edge; inspect for clipping')
        if max(margins) > max(w, h) * .15:
            raise RuntimeError('Excessive blank border after native page compaction')
    qa = {'png_size': [w, h], 'content_bbox': list(bbox), 'margins_pixels': margins,
          'dpi_requested': figure['dpi'], 'needs_visual_inspection': True}
    if 'pdf' in files:
        import pymupdf
        with pymupdf.open(directory / files['pdf']) as document:
            p = document[0]
            qa.update(pdf_pages=len(document), pdf_images=len(p.get_images(full=True)),
                      pdf_vector_paths=len(p.get_drawings()), pdf_page_inches=[p.rect.width / 72, p.rect.height / 72])
            if len(document) != 1 or qa['pdf_images'] != 0 or qa['pdf_vector_paths'] == 0:
                raise RuntimeError('Expected a single-page native vector PDF without raster plot images')
    return qa

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doctor', action='store_true')
    parser.add_argument('--spec', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--formats', default='png,pdf,svg,emf')
    args = parser.parse_args()
    if args.doctor:
        result = doctor(); print(json.dumps(result, indent=2)); return 0 if result['origin_com_available'] and all(result['modules'].values()) else 1
    if args.spec is None:
        parser.error('--spec is required')
    figures, hashes = load_spec(args.spec)
    formats = args.formats.split(',')
    if any(v not in ('png', 'pdf', 'svg', 'emf') for v in formats):
        parser.error('Supported formats: png,pdf,svg,emf')
    if args.validate_only:
        print(json.dumps({'valid': True, 'figures': [f['id'] for f in figures], 'source_hashes': hashes}, indent=2)); return 0
    if args.output is None:
        parser.error('--output is required')
    out = new_directory(args.output)
    session = None
    reports = []
    try:
        session = OriginSession()
        for f in figures:
            directory = out / f['id']; directory.mkdir()
            reports.append(session.build(f, directory, formats))
            ensure_sources_unchanged(hashes)
            print('Verified native Origin graph:', f['id'], flush=True)
        write_json(out / 'manifest.json', {'complete': True, 'source_hashes': hashes, 'figures': reports})
    except Exception as error:
        write_json(out / 'failure.json', {'complete': False, 'error': str(error), 'completed_figures': [r['id'] for r in reports]})
        raise
    finally:
        if session is not None:
            write_json(out / 'origin_commands.json', session.log)
            session.close()
    return 0

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
