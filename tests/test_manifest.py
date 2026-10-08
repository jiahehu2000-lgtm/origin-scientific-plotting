"""Offline manifest/package checks; no Origin or Office installation needed."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/origin-scientific-plotting/scripts'))
from origin_to_ppt import load_manifest, ole_graphic_frames
from plot_spec import sha256

class ManifestTests(unittest.TestCase):
    def test_verified_project_and_later_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root / 'example'; folder.mkdir()
            project = folder / 'example.opju'; project.write_bytes(b'test fixture, not an Origin project')
            f = {'id': 'example', 'files': {'opju': 'example.opju'}, 'sha256': {'opju': sha256(project)},
                 'caption': 'Synthetic', 'graph_page': 'Figure'}
            manifest = root / 'manifest.json'; manifest.write_text(json.dumps({'complete': True, 'figures': [f]}))
            figures, hashes = load_manifest(manifest)
            self.assertEqual(figures[0]['project'], project)
            self.assertEqual(len(hashes), 2)
            project.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                load_manifest(manifest)

    def test_alternate_ole_markup_is_counted_as_one_frame(self):
        xml = '''<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"><p:graphicFrame>
        <mc:AlternateContent><mc:Choice><p:oleObj/></mc:Choice><mc:Fallback><p:oleObj/></mc:Fallback>
        </mc:AlternateContent></p:graphicFrame></p:sld>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fixture.pptx'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('ppt/slides/slide1.xml', xml)
            self.assertEqual(ole_graphic_frames(path), 1)

    def test_incomplete_manifest_is_not_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'manifest.json'; path.write_text('{"complete": false, "figures": []}')
            with self.assertRaises(ValueError):
                load_manifest(path)

if __name__ == '__main__':
    unittest.main()
