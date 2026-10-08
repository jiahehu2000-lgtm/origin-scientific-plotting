# Figure specification (schema version 1)

The JSON file contains `{"schema_version": 1, "figures": [...]}`. Supply data and axis ranges explicitly. Paths to CSV files are relative to the specification file, not the working directory. UTF-8 CSV files need unique headers and finite numbers in all referenced columns. The helper checks hashes of the JSON and referenced CSV files after plotting.

## XY figures

```json
{
  "id": "response",
  "kind": "xy",
  "caption": "Description and source of this figure.",
  "page_inches": [4, 3],
  "font_family": "Arial",
  "font_size_pt": 13,
  "axis_width_pt": 1,
  "dpi": 600,
  "xaxis": {"label": "Time (s)", "limits": [0, 2], "increment": 0.5, "decimals": 1},
  "yaxis": {"label": "Current (nA)", "limits": [0, 1], "increment": 0.2, "decimals": 1},
  "series": [
    {"kind": "scatter", "label": "Measured", "color": "#6699CC", "csv": {"path": "data.csv", "x": "time_s", "y": "current_nA"}},
    {"kind": "line", "label": "Supplied fit", "x": [0, 1, 2], "y": [0.9, 0.2, 0.04], "color": "#F14040"}
  ],
  "legend": {"x": 1.3, "y": 0.8},
  "annotations": [{"text": "Condition A", "x": 1.3, "y": 0.5}]
}
```

- `id`: unique portable filename, up to 64 letters/digits/underscores/hyphens; starts with a letter/digit.
- `series.kind`: `line`, `scatter`, `errorbar`, or `bar`. Use inline `x`, `y` arrays **or** `csv` column mappings. Error bars also require nonnegative symmetric `yerr` values or a CSV `yerr` column mapping.
- `color`: `#RRGGBB`. `line_width_pt` defaults to 1; `marker_size_pt` defaults to 4; `marker` is `none`, `circle`, `square`, or `triangle`; `dash` is `solid`, `dash`, `dot`, or `dashdot`.
- `bar_width`: positive width in x-axis units, default 0.6. Positions must be unique and increasing. Use evenly spaced positions for a consistent column width.
- Axis `scale`: `linear` (default) or `log`. Log ranges and data must be positive; major ticks use the supplied increment. Inspect logarithmic tick appearance in your Origin version.
- Optional axis `labels`: categorical ticks such as `["BIN", "LIN", "TANH"]`. The helper supports single-token labels with a linear axis and increment 1. More complex labels need native Origin customization.
- `frame`: optional `[left, top, width, height]`, as fractions of the initial native page. Top is measured from the page's upper edge. Default XY frame is `[0.18, 0.06, 0.78, 0.72]`.
- Legend and annotation positions are data coordinates. The anchor must be within the axes; this does not guarantee that a long label fits. Verify rendered bounds visually.
- `caption` is separate from the graph and is carried into the verification report and optional PPT. A `title` key is deliberately rejected by this compact-layout helper. Use an in-frame annotation or customize the native graph if a top title is required.

The supplied fit is plotted as supplied; the tool does not estimate parameters. Error magnitudes are plotted as supplied; it does not calculate SD, SEM, or confidence intervals.

## Heatmaps and confusion matrices

```json
{
  "id": "confusion",
  "kind": "heatmap",
  "caption": "Row-normalized predictions; an untested class is missing.",
  "matrix": {
    "values": [[9, 1, 0], [0, 8, 2], [null, null, null]],
    "normalization": "row",
    "digits": 2,
    "annotate": true,
    "colorbar_label": "Proportion",
    "missing_row_label": "Not tested",
    "low_color": "#F7FBFF",
    "high_color": "#08306B",
    "missing_color": "#F1F1F1"
  }
}
```

Matrix values are **rows in displayed top-to-bottom order**. A confusion matrix uses true classes in rows and predicted classes in columns. The native matrix coordinate direction and reversed y-axis preserve that ordering. The script supplies square physical cells and a separate native colorbar layer. Custom page/frame dimensions must also produce square cells.

- `normalization`: `none` (default) or explicit `row`. Row normalization computes each value divided by its row total. The original counts remain in `original_matrix.csv` and `frozen_spec.json`.
- A whole row of `null`, or a zero-total count row under row normalization, becomes missing. Partially missing count rows cannot be normalized. Observed zeros stay numeric zero. Use `null`, never `NaN` in JSON.
- `limits`: optional increasing colorbar bounds, default `[0,1]` for row normalization. Bounds that would hide supplied values are rejected.
- Numbers are formatted with leading zero and `digits` decimal places; exact 0 and 1 are compact. Individual missing cells have no numerical label; a wholly missing row uses `missing_row_label`.
- Optional x/y `labels` must match the matrix dimensions. Heatmap x limits are `[0.5, columns+0.5]` and y limits `[rows+0.5, 0.5]`; full cell extents cannot be hidden by custom limits.

## Outputs and errors

Run `origin_plot.py --spec figures.json --output results`. `results` must be new or empty. Each figure gets its OPJU, PNG, PDF, EMF, SVG, native data CSV files, frozen specification, and verification JSON. SVG is a conversion of the Origin vector PDF, with glyphs converted to paths. `--formats png,pdf` selects fewer formats; a preview PNG is always produced.

`manifest.json` is written only after all figures pass. Failures write `failure.json` and a command log where available; already produced artifacts are preserved for diagnosis. Fix the cause and rerun in a new output directory. Reports include local paths and source hashes: review them before sharing them publicly.
