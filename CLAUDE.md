# CADathon Project Rules

## Focus

Terminal-driven, headless parametric 3D CAD modeling via `build123d`.
All scripts produce geometry programmatically, export to STEP/STP, and are
validated through the `verify_geometry.py` utility — no GUI required.

## Strategy

1. Construct massive base features first (solid bosses, pads, cylinders).
2. Apply strict sketch constraints (tangency, symmetry, alignment) at sketch time.
3. Execute subtraction shapes (cuts, holes) only after the base body is stable.
4. Apply cosmetic fillets/chamfers last, after all boolean operations settle.

## Guardrail — Mandatory Volume Verification

Every generated CAD script **must** be tested before marking a task complete:

```bash
python verify_geometry.py <output>.step
```

The script prints `VERIFIED_VOLUME: [number] mm³` and exits 0 only when the
STEP file contains a valid solid with positive volume. Any exit code ≠ 0 or
a missing/corrupt solid is a hard failure — fix the model, re-export, re-verify.

## Tech Stack

- **CAD kernel**: build123d (CadQuery / OpenCASCADE)
- **Geometry I/O**: CadQuery STEP importer/exporter
- **Math / analysis**: scipy, trimesh, shapely
- **Fabrication skills**: dfam-check, gcode, sendcutsend, bambu-labs
- **Robot / scene I/O**: URDF, SDF, SRDF
- **2D / DXF**: dxf skill

## Repository

Base: <https://github.com/earthtojake/text-to-cad>
Skills installed from `/skills/` subdirectories.
Plugin registry: `.claude-plugin/`
