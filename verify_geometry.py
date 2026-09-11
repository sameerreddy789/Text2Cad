#!/usr/bin/env python3
import os, sys, traceback

def verify_volume(path):
	import build123d as b
	if not os.path.isfile(path):
		raise FileNotFoundError(f"STEP file not found: {path}")
	result = b.import_step(path)
	if result is None:
		raise ValueError("Could not parse STEP file -- no valid solid found. Check for unconstrained wireframes or loose faces.")
	if hasattr(result, "val"):
		solid = result.val()
	else:
		solid = result
	volume = solid.volume
	if volume <= 0.0:
		raise ValueError(f"Parsed solid has non-positive volume ({volume}) -- likely an unconstrained wireframe or loose face.")
	return volume

def main():
	if len(sys.argv) < 2:
		print("Usage: python verify_geometry.py <file.step|file.stp>", file=sys.stderr)
		return 1
	path = sys.argv[1]
	try:
		volume = verify_volume(path)
		print(f"VERIFIED_VOLUME: {volume} mm3")
		return 0
	except ModuleNotFoundError as exc:
		print(f"[ERROR] Missing dependency: {exc}", file=sys.stderr)
		traceback.print_exc()
		return 1
	except Exception as exc:
		print(f"[ERROR] {type(exc).__name__}: {exc}", file=sys.stderr)
		traceback.print_exc()
		return 1

if __name__ == "__main__":
	sys.exit(main())
