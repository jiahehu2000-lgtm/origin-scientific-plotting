# Validation scope

This release was tested on a Windows desktop with OriginPro 2021, internal version **9.8002**, and Microsoft PowerPoint desktop, version **16.0**. Its four bundled figure specifications contain synthetic demonstration values only.

## Portable checks

Ten unit tests cover specification parsing, source-file hashes, rejection of negative error magnitudes and invalid log data, duplicate identifiers, explicit row normalization, preservation of original counts, missing/zero-observation rows, square cells, clipped color ranges, complete manifests, modified OPJU detection, and counting OLE graphic frames without counting alternate markup twice.

Skill frontmatter, UI metadata, reference links, required helper files, and Python syntax were checked locally. The skill also passed the Codex skill-creator validation helper. Hosted CI repeats the portable checks; it does not install or emulate Origin.

## Native Origin checks

All four examples were drawn through the actual Origin COM application:

| Example | Native result exercised |
| --- | --- |
| Response | Scatter points, a supplied reference line, editable legend and annotation |
| Error bars | Supplied symmetric error magnitudes and a connected line |
| Columns | Native columns with categorical tick labels |
| Confusion matrix | Row-normalized values, cell annotations, native colorbar, gray missing row |

For each figure the saved OPJU was reopened. The numeric tables, axis ranges/increments, visible tick-label sides, native font sizes/family, axis-frame widths, editable title/label strings, and missing-data color were checked. Physical data-frame dimensions were preserved within **0.0025 inch**, allowing Origin's native geometry rounding; text point sizes remained unchanged.

Origin exported PNG, PDF, and EMF. Each PDF was checked as a single page with vector paths and no raster plot images. SVG was derived from that PDF. PNGs were visually inspected for legends, labels, orientation, missing values, page borders, and excessive blank space. Public preview images are direct exports of the synthetic examples.

## Journal-selection gallery update (2026-10-09)

Four additional synthetic examples were drawn in the same actual Origin version: time response, independent observations, paired observations, and a normalized confusion matrix with an untested class. Every saved OPJU was reopened and its numbers, native geometry and typography verified. The final PNGs were visually inspected after relocating two annotations that initially crossed the axis frame.

Native settings are Arial 7 pt. All four exported PDFs contain vector paths and extractable ArialMT text, with no embedded raster plot images; actual PDF font metrics are approximately 6.958–6.959 pt. Actual compacted export widths differ from the initial canvases and are recorded rather than being advertised as fixed journal column widths. Public [gallery downloads](journal-gallery/README.md) and [verification summary](journal-gallery/validation.json) contain only synthetic data and no local source paths.

The new journal-style reference and specifications passed skill metadata/reference validation, the skill-creator validator, the existing ten unit tests, and offline specification validation. Hosted CI checks both example specifications; it does not run licensed Origin. Source conflicts and unavailable Cell-specific instructions remain explicit in the [Chinese guide](CNS期刊风格与选图指南.md).

## PowerPoint checks

The four graphs were copied from Origin as OLE objects and placed in a two-slide deck. All four reopened objects had shape type 7 and `Origin95.Graph`, were embedded rather than linked, retained a 5 cm width, and had their aspect ratio locked. Slide previews were inspected.

Appending the four graphs to a copy of that deck produced four slides and eight native OLE graphic frames. The original slides' shapes/text/geometry and embedded payload hashes were preserved; the source deck and OPJU file hashes did not change.

One confusion-matrix object was **double-clicked in desktop PowerPoint** and opened in the native Origin editor. The editable graph, matrix-backed layer, colorbar, and cell annotations were visible. This verifies one interactive example in the tested environment; it is not a claim that activation was tested for every object or on another computer. The helper itself reports `interactive_editing_tested: false` because it does not automate this manual check.

## Limits

- Other Origin/Office releases, operating-system locales, fonts, and uncommon graph types were not exhaustively tested.
- Basic logarithmic axes are supported by the schema; a dedicated native log-axis demonstration is not included in this validation set.
- Unsupported plots, asymmetric uncertainties, grouped/stacked columns, multi-panel scientific layouts, and complex categorical labels need native Origin customization and their own verification.
- The batch helper creates new projects. It is not a general automatic editor for every existing OPJU.
- Numerical verification cannot establish a scientific model's validity or that a test set is independent. Those decisions remain with the researcher.
- Visual preview inspection is still necessary; automated margin checks alone cannot prove that every label fits.

No private research files or workstation paths are needed to run these examples.
