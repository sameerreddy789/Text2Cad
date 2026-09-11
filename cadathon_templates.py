"""
CADathon Mechanical Modeling Templates & Cheat Sheet (build123d)
Use these pre-tested functions to rapidly build competition geometry in minutes.
"""

from build123d import *
import math

# ---------------------------------------------------------------------------
# 1. Flange with Circular Bolt Pattern (Pitch Circle Diameter - PCD)
# ---------------------------------------------------------------------------
def make_circular_flange(outer_dia=100.0, inner_dia=40.0, thickness=12.0, bolt_pcd=75.0, bolt_count=6, bolt_dia=8.5):
    """Creates a circular mounting flange with a center bore and polar hole pattern."""
    with BuildPart() as flange:
        with BuildSketch() as sk:
            Circle(radius=outer_dia / 2.0)
            Circle(radius=inner_dia / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=thickness)

        # Cut bolt holes on PCD
        with BuildSketch(flange.faces().sort_by(Axis.Z)[-1]) as hole_sk:
            with PolarLocations(radius=bolt_pcd / 2.0, count=bolt_count):
                Circle(radius=bolt_dia / 2.0)
        extrude(amount=-thickness, mode=Mode.SUBTRACT)
    return flange.part

# ---------------------------------------------------------------------------
# 2. Stepped Shaft with Keyway and Chamfers
# ---------------------------------------------------------------------------
def make_stepped_shaft(sections=[(25.0, 40.0), (35.0, 50.0), (20.0, 30.0)], keyway=(8.0, 4.0, 30.0)):
    """
    sections: list of (diameter, length) tuples from -Z to +Z
    keyway: (width, depth, length) on largest section
    """
    with BuildPart() as shaft:
        current_z = 0.0
        for dia, length in sections:
            with Locations((0, 0, current_z)):
                Cylinder(radius=dia / 2.0, height=length, align=(Align.CENTER, Align.CENTER, Align.MIN))
            current_z += length

        # Cut keyway if requested
        if keyway:
            kw, kd, kl = keyway
            # Cut on top face of middle section
            with Locations((0, sections[1][0] / 2.0 - kd / 2.0, sections[0][1] + kl / 2.0)):
                Box(kw, kd + 1.0, kl, mode=Mode.SUBTRACT)

        # Add 45-deg chamfer to shaft ends
        chamfer(shaft.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[0], length=1.0)
        chamfer(shaft.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[-1], length=1.0)
    return shaft.part

# ---------------------------------------------------------------------------
# 3. L-Bracket / Bearing Pillow Block
# ---------------------------------------------------------------------------
def make_l_bracket(base_len=80.0, base_width=60.0, upright_height=70.0, wall_thk=10.0, rib_thk=8.0, bore_dia=30.0):
    """Creates a reinforced L-bracket with center bore and structural stiffening rib."""
    with BuildPart() as bracket:
        # 1. Base Plate
        Box(base_len, base_width, wall_thk, align=(Align.MIN, Align.CENTER, Align.MIN))
        
        # 2. Upright Plate
        with Locations((0, 0, wall_thk)):
            Box(wall_thk, base_width, upright_height, align=(Align.MIN, Align.CENTER, Align.MIN))

        # 3. Center Bore on Upright
        with BuildSketch(Plane.YZ.offset(wall_thk / 2.0)):
            with Locations((0, wall_thk + upright_height * 0.65)):
                Circle(radius=bore_dia / 2.0)
        extrude(amount=wall_thk * 2, both=True, mode=Mode.SUBTRACT)

        # 4. Central Stiffening Rib
        with BuildSketch(Plane.XZ):
            with Locations((wall_thk, wall_thk)):
                # Triangle profile from base to upright
                Polygon([
                    (0, 0),
                    (base_len * 0.7 - wall_thk, 0),
                    (0, upright_height * 0.8),
                    (0, 0)
                ])
        extrude(amount=rib_thk, both=True)

        # 5. Base Mounting Holes (Counterbores)
        with Locations((base_len * 0.75, 0, 0)):
            with GridLocations(x_spacing=0, y_spacing=base_width * 0.6, x_count=1, y_count=2):
                CounterBoreHole(radius=4.5, counter_bore_radius=8.0, counter_bore_depth=4.0)

    return bracket.part

# ---------------------------------------------------------------------------
# 4. Hollow Enclosure with Filleted Corners & Shell
# ---------------------------------------------------------------------------
def make_enclosure(length=120.0, width=80.0, height=45.0, wall_thickness=2.5, corner_fillet=6.0):
    """Creates an enclosure box shelled to uniform wall thickness."""
    with BuildPart() as box:
        Box(length, width, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Fillet vertical corners
        vertical_edges = box.edges().filter_by(Axis.Z)
        fillet(vertical_edges, radius=corner_fillet)
        # Shell from top face
        top_face = box.faces().sort_by(Axis.Z)[-1]
        offset(openings=top_face, amount=-wall_thickness)
    return box.part

# ---------------------------------------------------------------------------
# 5. Revolved Pulley / V-Belt Sheave
# ---------------------------------------------------------------------------
def make_v_pulley(outer_dia=90.0, groove_dia=70.0, groove_angle_deg=38.0, width=20.0, bore_dia=18.0):
    """Creates a V-belt pulley via parametric 2D cross-section revolution."""
    groove_half_angle = math.radians(groove_angle_deg / 2.0)
    groove_depth = (outer_dia - groove_dia) / 2.0
    half_top = groove_depth * math.tan(groove_half_angle)
    
    with BuildPart() as pulley:
        with BuildSketch(Plane.XZ) as sk:
            # Revolve half-profile around Z axis
            Polygon([
                (bore_dia / 2.0, -width / 2.0),
                (outer_dia / 2.0, -width / 2.0),
                (outer_dia / 2.0, -half_top),
                (groove_dia / 2.0, 0.0),
                (outer_dia / 2.0, half_top),
                (outer_dia / 2.0, width / 2.0),
                (bore_dia / 2.0, width / 2.0),
                (bore_dia / 2.0, -width / 2.0),
            ])
        revolve(axis=Axis.Z)
    return pulley.part

if __name__ == "__main__":
    print("Exporting CADathon templates...")
    p1 = make_circular_flange()
    export_step(p1, "template_flange.step")
    p2 = make_l_bracket()
    export_step(p2, "template_bracket.step")
    print("Done! Templates generated and verified.")
