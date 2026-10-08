# Native Origin workflow and layout repair

## What counts as an Origin graph

Use a native graph page backed by worksheets or matrices. The OPJU must reopen with numerical data and editable axes, plots, and labels. A PNG pasted into an Origin page is a picture and does not meet this requirement. Likewise, a PDF containing a rasterized graph does not become a vector graph because of its extension.

For a new supported graph use the JSON helper. For an existing project, load a copy in a separate COM instance, inspect its graph pages and numerical tables, then modify those native objects. Do not rebuild an existing complex graph from a screenshot or let a batch helper silently discard special formatting.

## Source preservation and native APIs

`win32com.client.DispatchEx('Origin.Application')` creates the automation instance used by the helper. Do not attach to or close the user's active Origin window. `NewProject`, `Load`, `Save`, `Execute`, `Evaluate`, `PutWorksheet`/`GetWorksheet`, and `PutMatrix`/`GetMatrix` are the core operations. Check return values and reopen saved projects before making success claims. COM availability depends on installed Origin and its licensing/registration.

Use `SetLTStr`/`GetLTStr` for user text and paths rather than interpolating arbitrary strings into executable LabTalk. Numeric arrays use double-precision COM variants. Origin's native missing numeric value is `-1.23456789e-300`; the helper translates explicit missing cells to that value and back to blank CSV entries.

Useful implementation details:

- Origin can report success for `label -xb " "` while creating no editable title. Create a nonempty placeholder, then assign the actual text through the COM string property.
- Origin's default font scaling can change typography when page geometry changes. Explicitly set `layer.factor=1` and verify native axis and label sizes after saving/reopening.
- Disable graph Speed Mode for full-resolution exports and check the saved data arrays.
- Some versions do not redraw text positions while hidden. Redraw the automation window briefly before export; do not take a screenshot of a stale hidden graph as final evidence.
- Missing heatmap values need `layer.cmap.colorMiss`. Assigning a visual gray label over numeric zeros is not a correct missing-data representation.

## Removing a title without leaving a blank band

Work on the OPJU copy. Delete only the requested native title/annotation. Determine the content bounds from an Origin preview, then compact the **native page** and reposition all native layers together while keeping their physical frame dimensions. Preserve font sizes, label text, and plotted values. Export all formats again from this corrected project.

The batch helper uses this approach automatically: it measures the native PNG's nonwhite bounds, gives the content a small margin, updates the page and layer positions, saves, reopens, and verifies. This is a layout operation, not a crop of just the output PNG. Inspect all four sides afterward: a passing margin check cannot detect every overlap or clipped descender.

When using Origin's GUI, inspect Plot Details for the page/layer dimensions, layer font scaling, and axis labels. If the data frame itself needs a new aspect ratio, change that ratio explicitly and recheck labels. Do not squeeze a square confusion matrix into a rectangle.

## Font size at final publication width

A graph with 13 pt native text on a 10 cm-wide page has about 6.5 pt text when placed at 5 cm width. Use the expected final placement width and compare against neighboring panels. Nominally equal Origin font sizes can look different if page widths differ.

Do not automatically make all plots 13 pt or all PPT placements 5 cm. Those are configurable examples. Match the user's reference, preserve requested proportions, and inspect at the actual final size. Shorten an oversized annotation with approval of its meaning, or reposition it; do not reduce all fonts simply to force a label to fit.

## Verification boundaries

For supported plots the helper checks saved numerical arrays, native axis fonts/frame widths, editable label strings, missing-data color, PNG margins, and PDF vector paths/no raster plot images. It leaves `needs_visual_inspection=true`: an agent must open the PNGs and assess tick labels, line/marker contrast, text overlap, page borders, and consistent final-size typography.

The examples exercise only basic supported chart types. Record the installed version tested, not a broad claim that every Origin release, locale, installed font, or graph type is compatible. If a native command fails, retain the logs, consult the primary documentation, and adapt or disclose the limitation. Do not quietly fall back to another plotting library while claiming Origin output.

Sources: [Origin COM](https://docs.originlab.com/com/classes/application/), [text labels](https://docs.originlab.com/labtalk/ref/label-cmd/), [native exports](https://docs.originlab.com/labtalk/tutorials/tutorial-graphing-and-exporting-with-lt/), [colormap/missing-data properties](https://docs.originlab.com/labtalk/ref/layer-cmap-obj/).
