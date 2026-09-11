#!/usr/bin/env python3
"""
CADathon Rapid Modeling Workspace (IIT Bhubaneswar - Tech Zephyr 4.0)
Pre-configured with build123d, bd_warehouse, ocp_vscode, and Trimesh.

How to use during the competition:
1. Write your modeling logic inside the `build_model()` function.
2. Run this script to test, inspect volume, and view live in VS Code (if ocp-vscode installed).
3. Run `python cadathon_runner.py workspace_cadathon.py` to auto-generate the submission package!
"""

import sys
import math
from build123d import *
import bd_warehouse as bdw

# Optional live VS Code 3D viewer integration
try:
    from ocp_vscode import show, show_object, set_defaults, reset_show
    HAS_OCP_VSCODE = True
except ImportError:
    HAS_OCP_VSCODE = False

def build_model():
    """
    Define your competition geometry here.
    Uses parametric constraints, named datums, and build123d Joints.
    """
    with BuildPart() as part:
        # Example Base Feature
        Box(50, 40, 15, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Example Cylindrical Boss with Through Bore
        with Locations((0, 0, 15)):
            Cylinder(radius=15, height=20, align=(Align.CENTER, Align.CENTER, Align.MIN))
            Cylinder(radius=8, height=35, mode=Mode.SUBTRACT, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Example Mounting Holes on Base
        with Locations((0, 0, 0)):
            with GridLocations(x_spacing=35, y_spacing=26, x_count=2, y_count=2):
                CounterBoreHole(radius=3.0, counter_bore_radius=5.5, counter_bore_depth=3.0)

        # Example Fillet
        # Fillet bottom edges safely
        # fillet(part.edges().filter_by(Axis.Z), radius=3.0)

    return part.part

if __name__ == "__main__":
    print("[*] Building CADathon model...")
    model = build_model()
    
    # 1. Exact Volume Verification
    volume_mm3 = model.volume
    volume_cm3 = volume_mm3 / 1000.0
    bbox = model.bounding_box()
    
    print("\n" + "=" * 50)
    print(f"  VERIFIED VOLUME: {volume_mm3:.6f} mm³ ({volume_cm3:.6f} cm³)")
    print(f"  BOUNDING BOX   : {bbox.size.X:.2f} × {bbox.size.Y:.2f} × {bbox.size.Z:.2f} mm")
    print(f"  SURFACE AREA   : {model.area:.2f} mm²")
    print(f"  TOPOLOGY       : {len(model.faces())} Faces | {len(model.edges())} Edges | {len(model.vertices())} Vertices")
    print("=" * 50 + "\n")

    # 2. Export test STEP
    export_step(model, "current_solution.step")
    print("[+] Exported current_solution.step")

    # 3. Live OCP VS Code Viewer if active
    if HAS_OCP_VSCODE:
        try:
            show(model, reset_camera=False)
            print("[+] Sent model to OCP CAD Viewer in VS Code")
        except Exception:
            pass
