#!/usr/bin/env python3
"""
Generate a 10mm x 10mm x 10mm parametric cube and export to test.step.
Uses build123d (OCP) — the repo's primary CAD backend.
"""

from build123d import Box, export_step

cube = Box(10.0, 10.0, 10.0)
export_step(cube, "test.step")
print("Exported test.step")
