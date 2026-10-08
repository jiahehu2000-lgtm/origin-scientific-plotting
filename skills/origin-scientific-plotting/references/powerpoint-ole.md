# Editable Origin graphs in PowerPoint

Use this route when double-clicking a graph should open Origin. Requires installed desktop PowerPoint and Origin on Windows. A PNG, PDF, SVG, or pasted EMF picture remains a picture. It does not satisfy Origin editing even if it looks identical.

## Native clipboard route

1. Load the saved OPJU in a separate Origin instance and activate the requested graph page.
2. Call `Origin.CopyPage(graph_name, 4)`: Origin documents format 4 as an **OLE Object**.
3. In PowerPoint use `Shapes.PasteSpecial(DataType=10, DisplayAsIcon=0, Link=0)`. `10` is `ppPasteOLEObject`; `Link=0` creates an embedded object.
4. Check shape type 7 and an `OLEFormat.ProgID` beginning with `Origin`. Read the clipboard EMF frame to determine the object's native cached aspect ratio.
5. Set physical width, compute height from that ratio, then enable `LockAspectRatio`. Inspect the resulting slide at the final width.

The helper reads the complete plotting manifest:

```powershell
python <skill-dir>/scripts/origin_to_ppt.py --manifest results/manifest.json --output figures.pptx --width-cm 5
python <skill-dir>/scripts/origin_to_ppt.py --manifest results/manifest.json --template existing.pptx --output extended.pptx --width-cm 5
```

`--template` appends slides to a copy of an existing deck. Existing slides and embedded OLE payloads are checked for preservation. The source PPT and OPJU files are hashed and never overwritten. Do not use the source filename as the output filename. Output, preview, and verification paths must be new.

Two figures are placed on each new slide, each with its figure id and caption. Width, title, caption font, and font sizes are configurable. Long captions fail the text-fit check rather than silently shrinking. Adjust wording or the explicitly supplied typography/layout and rerun in a new destination.

## Native PowerPoint details

- A newly added text box may inherit `TextFrame2.AutoSize=1`, even after `TextFrame.AutoSize=0`. Disable both and restore its requested rectangle after setting font properties. Check `TextRange.BoundHeight` against the final rectangle.
- PowerPoint may be a shared application instance. Close only presentations opened by the helper; call `Quit` only when no other presentations remain.
- PowerPoint XML can contain duplicate `p:oleObj` references in alternate representations. Count unique native graphic frames/embedded object relationships, not raw occurrences of the tag.
- `ProgID` and embedding checks confirm structure, not successful activation on another computer. Double-click or invoke the `Edit`/`Open` OLE verb in PowerPoint and confirm Origin opens the embedded graph before claiming interactive editing was tested.
- A recipient still needs installed compatible Origin to edit the object. A cached graph image may display without Origin; that does not mean the embedded editor is available.
- The helper exports native slide previews for inspection and writes a separate verification report. It does not change the user's research data or run an RC model.

Sources: [Origin CopyPage format table](https://docs.originlab.com/com/classes/application/copypage/), [PowerPoint PasteSpecial](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.shapes.pastespecial).
