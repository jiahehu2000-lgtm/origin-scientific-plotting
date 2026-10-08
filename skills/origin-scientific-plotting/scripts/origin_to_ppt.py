"""Embed native editable Origin graphs in a new PPTX or append to a copy."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import time
import zipfile
import xml.etree.ElementTree as ET

from plot_spec import ensure_sources_unchanged, new_directory, sha256, write_json

PT_PER_CM = 72 / 2.54

def embedded_hashes(path):
    import hashlib
    with zipfile.ZipFile(path) as archive:
        return Counter(hashlib.sha256(archive.read(name)).hexdigest()
                       for name in archive.namelist() if name.startswith('ppt/embeddings/'))

def ole_graphic_frames(path):
    ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
    with zipfile.ZipFile(path) as archive:
        return sum(1 for name in archive.namelist()
                   if name.startswith('ppt/slides/slide') and name.endswith('.xml')
                   for frame in ET.fromstring(archive.read(name)).findall('.//p:graphicFrame', ns)
                   if frame.find('.//p:oleObj', ns) is not None)

def load_manifest(path):
    path = Path(path).resolve(strict=True)
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('complete') is not True or not manifest.get('figures'):
        raise ValueError('A complete, nonempty plotting manifest is required')
    hashes = {str(path): sha256(path)}
    figures = []
    for f in manifest['figures']:
        if not isinstance(f.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', f['id']):
            raise ValueError('Invalid figure identifier in manifest')
        project = (path.parent / f['id'] / f['files']['opju']).resolve(strict=True)
        try:
            project.relative_to(path.parent)
        except ValueError:
            raise ValueError('Manifest project must stay within its output directory') from None
        actual = sha256(project)
        if actual != f['sha256']['opju']:
            raise ValueError('OPJU differs from verified manifest: ' + f['id'])
        hashes[str(project)] = actual
        figures.append({'id': f['id'], 'caption': f['caption'], 'project': project,
                        'graph': f['graph_page']})
    return figures, hashes

def slide_snapshot(slide):
    result = []
    for i in range(1, slide.Shapes.Count + 1):
        s = slide.Shapes(i)
        result.append({'name': s.Name, 'type': int(s.Type),
                       'geometry': [float(getattr(s, k)) for k in ['Left', 'Top', 'Width', 'Height']],
                       'text': s.TextFrame.TextRange.Text if s.HasTextFrame else None})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--template', type=Path)
    parser.add_argument('--width-cm', type=float, default=5)
    parser.add_argument('--font', default='Arial')
    parser.add_argument('--title', default='Origin scientific figures')
    parser.add_argument('--title-size-pt', type=float, default=32)
    parser.add_argument('--caption-size-pt', type=float, default=17)
    args = parser.parse_args()
    if sys.platform != 'win32':
        parser.error('Native Origin/PowerPoint OLE requires Windows')
    import pythoncom
    import win32com.client
    import win32clipboard
    import win32con

    figures, hashes = load_manifest(args.manifest)
    output = args.output.resolve()
    if output.suffix.lower() != '.pptx' or output.exists():
        parser.error('Output must be a new .pptx file')
    if args.width_cm <= 0 or args.title_size_pt <= 0 or args.caption_size_pt <= 0:
        parser.error('Width and font sizes must be positive')
    output.parent.mkdir(parents=True, exist_ok=True)
    build = new_directory(output.parent / (output.stem + '_verification'))
    template = args.template.resolve(strict=True) if args.template else None
    prior_hashes = embedded_hashes(template) if template else Counter()
    if template:
        hashes[str(template)] = sha256(template)
    origin = ppt = deck = None
    records = []; prior_slides = []

    def retry(fn):
        for i in range(5):
            try:
                return fn()
            except pythoncom.com_error:
                if i == 4:
                    raise
                pythoncom.PumpWaitingMessages(); time.sleep(.3)

    def textbox(slide, name, value, x, y, w, h, size, bold=False):
        box = slide.Shapes.AddTextbox(1, x, y, w, h)
        box.Name = name
        tf = box.TextFrame
        tf.AutoSize = 0; tf.WordWrap = -1
        tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
        tf.TextRange.Text = value
        tf.TextRange.Font.Name = args.font
        tf.TextRange.Font.Size = size
        tf.TextRange.Font.Bold = -1 if bold else 0
        tf.TextRange.Font.Color.RGB = 0x222222
        box.TextFrame2.AutoSize = 0; tf.AutoSize = 0
        box.Left, box.Top, box.Width, box.Height = x, y, w, h
        if tf.TextRange.BoundHeight > h + .5 or tf.TextRange.BoundWidth > w + 1:
            raise ValueError('Caption/title does not fit: ' + name)
        return box

    try:
        origin = win32com.client.DispatchEx('Origin.Application'); origin.Visible = 0
        ppt = win32com.client.DispatchEx('PowerPoint.Application')
        if template:
            working = build / 'working_copy.pptx'
            shutil.copy2(template, working)
            deck = ppt.Presentations.Open(str(working), False, False, False)
            prior_slides = [slide_snapshot(deck.Slides(i)) for i in range(1, deck.Slides.Count + 1)]
        else:
            deck = ppt.Presentations.Add(False)
            deck.PageSetup.SlideWidth = 960; deck.PageSetup.SlideHeight = 540
        W, H = float(deck.PageSetup.SlideWidth), float(deck.PageSetup.SlideHeight)
        margin = 30; gap = 30; col_width = (W - 2 * margin - gap) / 2
        width = args.width_cm * PT_PER_CM
        caption_width = col_width - width - 24
        if caption_width < 100 or H < 260:
            raise ValueError('Figure width or template page size leaves insufficient caption space')
        slide = None
        for index, f in enumerate(figures):
            if index % 2 == 0:
                slide = deck.Slides.Add(deck.Slides.Count + 1, 12)
                slide.FollowMasterBackground = 0
                slide.Background.Fill.Solid(); slide.Background.Fill.ForeColor.RGB = 0xFFFFFF
                textbox(slide, 'OSPTitle', args.title, margin, 28, W - 2 * margin, 58, args.title_size_pt, True)
            x = margin + (index % 2) * (col_width + gap)
            textbox(slide, 'OSPFigureId_' + f['id'], f['id'], x, 94, col_width, 28, 20, True)
            if not origin.NewProject() or not origin.Load(str(f['project']), True):
                raise RuntimeError('Origin failed to load verified project: ' + f['id'])
            # graph_name is from the verified helper manifest, not executable code.
            if f['graph'] != 'Figure':
                raise ValueError('Expected a helper-generated graph page named Figure')
            if not origin.Execute('win -a Figure; page.active=1;') or not origin.CopyPage('Figure', 4):
                raise RuntimeError('Native Origin OLE clipboard copy failed')
            pythoncom.PumpWaitingMessages(); time.sleep(.2)
            win32clipboard.OpenClipboard()
            try:
                emf = win32clipboard.GetClipboardData(win32con.CF_ENHMETAFILE)
            finally:
                win32clipboard.CloseClipboard()
            header = struct.unpack('<IIiiiiiiiiIIIIHHIIIiiii', emf[:88])
            ratio = (header[8] - header[6]) / (header[9] - header[7])
            height = width / ratio
            if height > H - 150:
                raise ValueError('Figure height does not fit: ' + f['id'])
            obj = retry(lambda: slide.Shapes.PasteSpecial(DataType=10, DisplayAsIcon=0, Link=0)).Item(1)
            if obj.Type != 7 or not obj.OLEFormat.ProgID.startswith('Origin'):
                raise RuntimeError('Pasted shape is not an embedded Origin OLE object')
            obj.Name = 'OSPOrigin_' + f['id']; obj.AlternativeText = f['caption']
            obj.LockAspectRatio = 0
            obj.Left, obj.Top, obj.Width, obj.Height = x, 140, width, height
            obj.LockAspectRatio = -1
            textbox(slide, 'OSPCaption_' + f['id'], f['caption'], x + width + 24, 140,
                    caption_width, H - 170, args.caption_size_pt)
            records.append({'id': f['id'], 'slide': int(slide.SlideIndex), 'shape': obj.Name,
                            'shape_type': int(obj.Type), 'progid': obj.OLEFormat.ProgID,
                            'width_cm': float(obj.Width) / PT_PER_CM, 'height_cm': float(obj.Height) / PT_PER_CM,
                            'lock_aspect_ratio': int(obj.LockAspectRatio), 'native_ratio': ratio,
                            'embedded': True, 'linked': False})
            print('Embedded native Origin object:', f['id'], flush=True)
        deck.SaveAs(str(output), 24)
        deck.Close(); deck = None
        ensure_sources_unchanged(hashes)
        if prior_hashes - embedded_hashes(output):
            raise RuntimeError('An original embedded payload changed')
        expected_frames = (ole_graphic_frames(template) if template else 0) + len(figures)
        if ole_graphic_frames(output) != expected_frames:
            raise RuntimeError('Saved native OLE frame count differs')
        deck = ppt.Presentations.Open(str(output), True, False, False)
        for i, expected in enumerate(prior_slides, 1):
            if slide_snapshot(deck.Slides(i)) != expected:
                raise RuntimeError('An original slide changed: ' + str(i))
        for record in records:
            obj = deck.Slides(record['slide']).Shapes(record['shape'])
            if obj.Type != 7 or not obj.OLEFormat.ProgID.startswith('Origin') or obj.LockAspectRatio != -1:
                raise RuntimeError('Reopened native Origin object verification failed')
            if abs(float(obj.Width) / PT_PER_CM - args.width_cm) > 1e-5:
                raise RuntimeError('Reopened object width differs')
        preview = build / 'slides'; preview.mkdir()
        deck.Export(str(preview), 'PNG', 1920, round(1920 * H / W))
        report = {'complete': True, 'figures_added': len(figures), 'slides_total': deck.Slides.Count,
                  'source_hashes': hashes, 'output_sha256': sha256(output), 'records': records,
                  'old_slides_and_embedded_payloads_preserved': True,
                  'native_ole_frames': expected_frames, 'preview_directory': 'slides',
                  'interactive_editing_tested': False, 'needs_visual_inspection': True}
        write_json(build / 'verification.json', report)
        print('Verified PPTX:', output, flush=True)
    except Exception as error:
        write_json(build / 'failure.json', {'complete': False, 'error': str(error), 'figures_pasted': len(records)})
        raise
    finally:
        if deck is not None:
            deck.Close()
        if origin is not None:
            origin.Exit()
        if ppt is not None:
            try:
                if ppt.Presentations.Count == 0:
                    ppt.Quit()
            except Exception:
                pass
    return 0

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
