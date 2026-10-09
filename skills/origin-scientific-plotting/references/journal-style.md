# Journal style and choosing a scientific plot

Read this reference when the user asks for Nature/Science/Cell-style figures, a journal-specific layout, or help choosing a graph type. It supplements native Origin plotting; it does not change numerical data or authorize new analyses.

## Resolve the target before claiming compliance

Use the exact journal, article type, submission stage, and final placement width. A series name alone is not a complete style specification. Follow an explicit supplied reference or editor instruction within the user's scope; cite its provenance instead of calling it a universal journal standard.

The public [Chinese guide and source register](https://github.com/jiahehu2000-lgtm/origin-scientific-plotting/blob/main/docs/CNS期刊风格与选图指南.md) was checked on **2026-10-09**. It is a dated starting point. Verify the target journal's official page when applying journal requirements. If a detail is inaccessible or official sources conflict, record the unknown/conflict, make a useful editable draft, and avoid claiming complete journal compliance.

Known distinctions from that dated check:

| Target / source | Width and typography | Boundary |
|---|---|---|
| [Nature final](https://www.nature.com/nature/for-authors/final-submission) | 89/183 mm; ordinary text 5–7 pt; bold upright lowercase panel letters 8 pt; lines 0.25–1 pt | Initial-submission advance advice and other Nature journals differ |
| [Nature Communications](https://www.nature.com/ncomms/submit/how-to-submit) | 88/180 mm; thinnest line ≥1 pt; lowercase bold panels same size as other lettering | No numerical text size verified on that page |
| [Science webpage](https://www.science.org/content/page/instructions-preparing-initial-manuscript#preparation-of-figures) | 57/121/184 mm; about 7 pt, at least 5 pt; uppercase bold panels 10 pt; lines ≥0.5 pt | Official [2025 PDF](https://www.science.org/cms/asset/67f37ac8-4d02-4625-8a05-230568cb8323/author_prep_guide_2025.pdf) instead gives 90/183 mm, text 6–9 pt and lines ≥0.28 pt; priority not resolved |
| [Science Advances 2026 PDF](https://www.science.org/cms/asset/76887697-528f-4a22-afea-cee904504e76/sciadv_guide_to_preparing_figures_2026.pdf) | 90/184 mm; default 8 pt, minimum 6 pt; uppercase bold panels 9 pt; lines ≥0.28 pt | Contains raster-resolution inconsistencies; preserve editable vectors and check production instructions |
| [Cell / Cell Press](https://www.cell.com/information-for-authors/figure-guidelines) | Current journal-specific numbers unverified in this check (403) | Do not substitute Elsevier general examples or historical graphical-abstract rules |

SciencePlots and cnsplots are useful third-party style projects, not journal approval authorities. Do not claim that a shared color palette, a 5 cm graph width, or one font preset is mandatory for all three families.

## Choose by scientific relationship

These are practical recommendations, not universal submission requirements:

- **Time/order:** line plus measured markers where useful; do not silently bridge missing intervals or connect unordered categories.
- **Measured versus supplied model:** scatter plus model line; residuals only if supplied/authorized. Plotting must not silently refit.
- **Independent small groups:** individual points, optionally supplied central estimates/error bars. Counts can use zero-based columns; a continuous sample should not lose its distribution merely to match a bar-chart reference.
- **Paired observations:** connect only genuine matching IDs. Keep pair count distinct from total point count.
- **Large distributions:** box/violin plus points, or histogram/ECDF as appropriate. Explain whiskers, binning or density settings; do not remove outliers for appearance.
- **Nested repeats:** distinguish independent experiments from within-experiment measurements, as in SuperPlots. Do not invent independence from visible dots.
- **Matrices:** sequential color for ordered magnitude (including signed values where appropriate), diverging color for deviations about a meaningful center; keep missing distinct from zero. Use shared color limits for comparisons.
- **Confusion matrices:** preserve complete prediction labels, explicit count or row normalization, square cells, readable annotations, row sample counts, and missing/untested categories. Never remove mistaken predictions to make a smaller matrix appear more accurate.
- **Many curves:** consider consistent-axis small multiples. Use 3D for meaningful spatial/geometry or continuous-field coordinates, not merely to give ordinary columns numerical height and perspective.

Method sources: [Weissgerber et al.](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002128), [SuperPlots](https://rupress.org/jcb/article/219/6/e202001064/151717/SuperPlots-Communicating-reproducibility-and), [Error bars in experimental biology](https://rupress.org/jcb/article/177/1/7/34602/Error-bars-in-experimental-biology). Require the supplied meaning of n and SD/SEM/CI before drawing statistical labels. Do not compute significance simply because a plotting style supports it.

Cross-validation folds have correlated errors because training data overlap. Fold-to-fold SD may be descriptive; do not automatically treat the number of folds as independent n to compute SEM, confidence intervals or significance. See [Bengio & Grandvalet, 2004](https://www.jmlr.org/papers/v5/grandvalet04a.html).

The current batch helper supports line, scatter, symmetric supplied error bars, columns and basic annotated heatmaps. Box/violin, histograms/ECDF, native multi-panel layouts, forest/ROC plots, diverging-center heatmaps, asymmetric intervals and ribbons need separate native Origin adaptation and verification. Read `figure-spec.md` before assuming a schema field exists.

## Style at the final size

Keep condition colors consistent across figures and provide shape/line cues as well as color. Check grayscale and final-size legibility; a palette name alone does not establish accessibility. Compact native Origin pages without clipping labels, legends or error bars.

The helper's `page_inches` is an **initial** canvas. Native compaction changes the exported width while preserving point sizes. Read `compact_page.page_after_inches` and `export_qa.pdf_page_inches` from verification; use the actual exported width in placement calculations:

```text
placed_font_pt = source_font_pt * placement_width / actual_export_width
required_source_font_pt = desired_placed_font_pt * actual_export_width / placement_width
```

For example, 7 pt at 89 mm becomes about 3.93 pt at 50 mm. A fixed 5 cm placement is a user layout choice, not a journal standard. Re-layout a dense matrix or use a larger panel when needed. Preserve the user's text/font unless they authorize a typography change.

## Native outputs and claims

Prefer Origin PDF with vector paths **and editable text** for statistical plots. Check text extraction/fonts and embedded raster resolution, not only file suffix. Keep OPJU for editing; it is not a universal journal submission format. The helper's converted SVG may outline glyphs and must not be described as editable text where the target forbids outlines. A PPT image is not Origin OLE; a PPT deck is not automatically a permitted journal figure file.

Treat photos and mixed artwork separately from pure vector plots. Effective raster resolution depends on original pixel count and final size; changing DPI metadata or upsampling cannot restore detail. Preserve source links and unresolved conflicts in the delivery note. The numerical/native verification report proves those checks, not scientific validity or journal acceptance.
