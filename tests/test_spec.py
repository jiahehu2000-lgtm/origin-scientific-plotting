"""Portable validation tests. Native Origin checks are separate, on Windows."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/origin-scientific-plotting/scripts'))
from plot_spec import load_spec, normalize_rows, validate_figure, new_directory, ensure_sources_unchanged, sha256
from origin_plot import colorbar_tick_decimals

class SpecTests(unittest.TestCase):
    def setUp(self):
        self.examples = json.loads((ROOT / 'examples/figures.json').read_text())
        self.base = ROOT / 'examples'

    def test_example_schema_and_source_integrity(self):
        figures, hashes = load_spec(self.base / 'figures.json')
        self.assertEqual(len(figures), 4)
        self.assertEqual(len(hashes), 2)
        ensure_sources_unchanged(hashes)

    def test_normalization_retains_raw_counts_and_marks_zero_row(self):
        f = validate_figure(self.examples['figures'][3], self.base, {})
        self.assertEqual(f['matrix']['original_values'][0], [9, 1, 0, 0])
        self.assertEqual(f['matrix']['values'][0], [.9, .1, 0, 0])
        self.assertEqual(f['matrix']['values'][3], [None] * 4)
        self.assertEqual(f['yaxis']['limits'], [4.5, .5])
        w, h = f['page_inches']; _, _, fw, fh = f['frame']
        self.assertAlmostEqual(w * fw, h * fh)

    def test_missing_counts_cannot_be_normalized_as_zero(self):
        for row in [[1, None], [-1, 2]]:
            with self.assertRaises(ValueError):
                normalize_rows([row])
        self.assertEqual(normalize_rows([[None, None]]), [[None, None]])

    def test_bad_errorbars_and_log_values_rejected(self):
        f = copy.deepcopy(self.examples['figures'][1])
        f['series'][0]['yerr'][0] = -1
        with self.assertRaises(ValueError):
            validate_figure(f, self.base, {})
        f = copy.deepcopy(self.examples['figures'][1])
        f['yaxis'].update(scale='log', limits=[.1, 1])
        f['series'][0]['y'][0] = 0
        with self.assertRaises(ValueError):
            validate_figure(f, self.base, {})

    def test_source_mutation_and_existing_outputs_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'source.csv'; p.write_text('before')
            hashes = {str(p): sha256(p)}; p.write_text('after')
            with self.assertRaises(RuntimeError):
                ensure_sources_unchanged(hashes)
            with self.assertRaises(FileExistsError):
                new_directory(tmp)

    def test_nonsquare_and_clipped_matrix_rejected(self):
        f = copy.deepcopy(self.examples['figures'][3])
        f['frame'] = [.15, .04, .7, .5]
        with self.assertRaises(ValueError):
            validate_figure(f, self.base, {})
        f.pop('frame'); f['matrix']['limits'] = [.2, 1]
        with self.assertRaises(ValueError):
            validate_figure(f, self.base, {})

    def test_nan_and_duplicate_identifiers_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'test.json'
            p.write_text('{"schema_version":1,"figures":[NaN]}')
            with self.assertRaises(ValueError):
                load_spec(p)
            doc = copy.deepcopy(self.examples)
            doc['figures'] = [doc['figures'][1]] * 2
            p.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                load_spec(p)

    def test_fractional_colorbar_ticks_are_not_rounded_into_duplicates(self):
        digits = colorbar_tick_decimals(0, 3)
        labels = [f'{i * 0.6:.{digits}f}' for i in range(6)]
        self.assertEqual(labels, ['0.0', '0.6', '1.2', '1.8', '2.4', '3.0'])
        self.assertEqual(len(set(labels)), 6)
        self.assertEqual(colorbar_tick_decimals(0, 1), 1)
        self.assertEqual(colorbar_tick_decimals(0, 100), 0)
        self.assertGreaterEqual(colorbar_tick_decimals(0.01, 0.04), 3)

if __name__ == '__main__':
    unittest.main()
