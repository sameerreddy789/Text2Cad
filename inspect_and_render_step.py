#!/usr/bin/env python3
"""
Inspect test.step and generate:
1. Detailed CAD geometry properties
2. High-resolution 3D render PNG with shaded faces and dimensions
3. Interactive 3D HTML viewer with OrbitControls
"""

import os
import sys
import json
import build123d as b
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def inspect_step(step_path):
    if not os.path.exists(step_path):
        raise FileNotFoundError(f"File not found: {step_path}")

    part = b.import_step(step_path)
    solid = part.val() if hasattr(part, "val") else part

    bbox = solid.bounding_box()
    volume = solid.volume
    area = solid.area
    faces = solid.faces()
    edges = solid.edges()
    vertices = solid.vertices()
    center_of_mass = solid.center()

    metrics = {
        "file": step_path,
        "volume_mm3": round(volume, 4),
        "surface_area_mm2": round(area, 4),
        "center_of_mass": [round(c, 3) for c in (center_of_mass.X, center_of_mass.Y, center_of_mass.Z)],
        "bounding_box_min": [round(c, 3) for c in (bbox.min.X, bbox.min.Y, bbox.min.Z)],
        "bounding_box_max": [round(c, 3) for c in (bbox.max.X, bbox.max.Y, bbox.max.Z)],
        "dimensions_xyz": [round(bbox.size.X, 3), round(bbox.size.Y, 3), round(bbox.size.Z, 3)],
        "face_count": len(faces),
        "edge_count": len(edges),
        "vertex_count": len(vertices),
    }

    print("=== CAD Geometry Inspection ===")
    print(json.dumps(metrics, indent=2))

    # --- Render 3D isometric visualization ---
    fig = plt.figure(figsize=(9, 8), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#0f172a")
    fig.patch.set_facecolor("#0f172a")

    # Extract triangulated mesh for plotting
    mesh_verts, mesh_triangles = solid.tessellate(tolerance=0.1)
    
    tri_coords = []
    for tri in mesh_triangles:
        tri_coords.append([(mesh_verts[idx].X, mesh_verts[idx].Y, mesh_verts[idx].Z) for idx in tri])

    # Plot 3D poly collection with cyan-blue futuristic theme
    collection = Poly3DCollection(
        tri_coords,
        facecolors="#38bdf8",
        alpha=0.85,
        edgecolors="#0284c7",
        linewidths=0.6,
    )
    ax.add_collection3d(collection)

    # Plot feature edges prominently
    for edge in edges:
        p1 = edge.start_point()
        p2 = edge.end_point()
        ax.plot([p1.X, p2.X], [p1.Y, p2.Y], [p1.Z, p2.Z], color="#38bdf8", linewidth=2.0, alpha=0.95)

    # Plot vertices
    vx = [v.X for v in vertices]
    vy = [v.Y for v in vertices]
    vz = [v.Z for v in vertices]
    ax.scatter(vx, vy, vz, color="#f59e0b", s=35, edgecolors="#ffffff", linewidths=0.8, zorder=5)

    # Set viewport bounds
    padding = 2.0
    ax.set_xlim([bbox.min.X - padding, bbox.max.X + padding])
    ax.set_ylim([bbox.min.Y - padding, bbox.max.Y + padding])
    ax.set_zlim([bbox.min.Z - padding, bbox.max.Z + padding])

    # Styling
    ax.set_title(
        f"test.step: Parametric Solid Cube\n"
        f"Volume: {volume:.1f} mm³ | Dimensions: {bbox.size.X:.1f} × {bbox.size.Y:.1f} × {bbox.size.Z:.1f} mm",
        color="#f8fafc",
        fontsize=13,
        pad=20,
        fontweight="bold",
    )
    ax.set_xlabel("X (mm)", color="#94a3b8", labelpad=10)
    ax.set_ylabel("Y (mm)", color="#94a3b8", labelpad=10)
    ax.set_zlabel("Z (mm)", color="#94a3b8", labelpad=10)
    ax.tick_params(colors="#94a3b8")
    ax.grid(color="#334155", linestyle="--", linewidth=0.5, alpha=0.7)

    # Isometric view angle
    ax.view_init(elev=28, azim=45)

    output_png = "test_step_render.png"
    plt.tight_layout()
    plt.savefig(output_png, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Rendered PNG saved to: {output_png}")

    # Also copy to artifact dir if present
    artifact_dir = r"C:\Users\samee\.gemini\antigravity-ide\brain\3c32c317-d495-4fbc-922a-a282c3e14b2f"
    if os.path.exists(artifact_dir):
        import shutil
        target_path = os.path.join(artifact_dir, "test_step_render.png")
        shutil.copyfile(output_png, target_path)
        print(f"Artifact image saved to: {target_path}")

    # --- Generate Interactive 3D HTML Viewer ---
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>test.step - 3D Interactive CAD Viewer</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      overflow: hidden;
      background-color: #0b0f19;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #e2e8f0;
    }}
    #canvas-container {{ width: 100vw; height: 100vh; }}
    .badge {{
      position: absolute;
      top: 20px;
      left: 20px;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 12px;
      padding: 16px 20px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
      max-width: 320px;
    }}
    .badge h1 {{ margin: 0 0 8px 0; font-size: 17px; color: #38bdf8; }}
    .badge p {{ margin: 4px 0; font-size: 13px; color: #94a3b8; }}
    .badge .val {{ color: #f8fafc; font-weight: 600; }}
    .hint {{ margin-top: 10px; font-size: 11px; color: #64748b; font-style: italic; }}
    .controls {{
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 30px;
      padding: 8px 18px;
      font-size: 12px;
      color: #94a3b8;
    }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
  <div class="badge">
    <h1>test.step 3D Solid</h1>
    <p>Volume: <span class="val">{volume:.1f} mm³</span></p>
    <p>Dimensions: <span class="val">{bbox.size.X:.1f} × {bbox.size.Y:.1f} × {bbox.size.Z:.1f} mm</span></p>
    <p>Surface Area: <span class="val">{area:.1f} mm²</span></p>
    <p>Faces: <span class="val">{len(faces)}</span> | Edges: <span class="val">{len(edges)}</span></p>
    <div class="hint">Left-click: Rotate | Right-click: Pan | Scroll: Zoom</div>
  </div>
  <div class="controls">Interactive Three.js Orbit View</div>
  <div id="canvas-container"></div>

  <script>
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b0f19);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(22, 18, 25);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.2);
    dirLight1.position.set(20, 30, 20);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xf59e0b, 0.6);
    dirLight2.position.set(-20, -10, -20);
    scene.add(dirLight2);

    // Grid
    const grid = new THREE.GridHelper(40, 20, 0x1e293b, 0x0f172a);
    grid.position.y = {bbox.min.Z};
    scene.add(grid);

    // Box Geometry
    const geometry = new THREE.BoxGeometry({bbox.size.X}, {bbox.size.Z}, {bbox.size.Y});
    const material = new THREE.MeshStandardMaterial({{
      color: 0x0284c7,
      metalness: 0.2,
      roughness: 0.3,
      transparent: true,
      opacity: 0.92,
    }});
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    // Outline wireframe edges
    const edgesGeom = new THREE.EdgesGeometry(geometry);
    const lineMat = new THREE.LineBasicMaterial({{ color: 0x38bdf8, linewidth: 2 }});
    const wireframe = new THREE.LineSegments(edgesGeom, lineMat);
    scene.add(wireframe);

    // Corner vertices
    const pointsGeom = new THREE.BufferGeometry();
    const positions = [
      -5, -5, -5,  5, -5, -5,  5,  5, -5, -5,  5, -5,
      -5, -5,  5,  5, -5,  5,  5,  5,  5, -5,  5,  5
    ];
    pointsGeom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    const pointsMat = new THREE.PointsMaterial({{ color: 0xfbbf24, size: 0.8 }});
    const points = new THREE.Points(pointsGeom, pointsMat);
    scene.add(points);

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }}
    animate();

    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }});
  </script>
</body>
</html>
"""
    html_file = "view_cube.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Interactive HTML viewer saved to: {html_file}")

if __name__ == "__main__":
    step = "test.step" if len(sys.argv) < 2 else sys.argv[1]
    inspect_step(step)
