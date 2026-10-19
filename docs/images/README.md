# Project media

The README uses generated renders because no photos or recordings of the physical build are available. All captions identify renders and simulation explicitly.

| File | Content |
| --- | --- |
| `robot-concept.png` | Illustrative robot layout using the included meshes, an inferred assembly, and generic motor bodies; 1600 × 900 |
| `cad-parts.png` | Six individual existing STL meshes; 1600 × 1050 |
| `solve-simulation.gif` | Smooth cube-only software solve using `kociemba` and the repository's cube model; 1000 × 660 |
| `solved-preview.png` | Final solved frame of the animation |
| `solve-sequence.json` | Reproducible scramble, facelets, solution, and solved-state verification |

Regenerate with `python scripts/render_media.py` after installing `scripts/requirements-media.txt`. This does not connect to the robot. Model colors, generic motor geometry, assembly placement, and animation timing are illustrative; the GIF does not animate the U/U′ hardware workaround.

## Checklist

- [x] Render an illustrative robot layout and label it as a render.
- [x] Render the existing printable parts.
- [x] Generate a simulated solve and verify its final cube state.
- [x] Provide image descriptions and captions in the main README.
- [ ] Confirm the mechanical files' original source, author, and redistribution terms.
- [ ] Optional: add a photo of the actual robot as `robot-photo.jpg`.
- [ ] Optional: add a short physical solve as `robot-solve.mp4` or `robot-solve.gif`.
- [ ] If actual media is added, update the README captions and keep simulation labels on generated media.

The optional filenames above are placeholders in this checklist, not broken image links or empty media files. No photos are required to use the current README. See [NOTICE.md](../../NOTICE.md) for mechanical-design attribution and license scope.
