#!/usr/bin/env python3
"""Emit pad complete-e2e runtime surfaces. Unknown flags fail-closed."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description="usage: list-surfaces.py [--project-dir PATH]")
    ap.add_argument("--project-dir", default="")
    args = ap.parse_args()
    root = Path(args.project_dir).resolve() if args.project_dir else ROOT
    if not root.is_dir():
        print("list-surfaces: project-dir not a directory", file=sys.stderr)
        return 2
    surfaces = [
        {"id": "capability:repository", "kind": "repository", "path": ".", "package_dir": "."},
        {"id": "capability:cli", "kind": "cli", "path": "scripts/complete-e2e/prove.py", "package_dir": "."},
        {"id": "capability:web-ui", "kind": "web-ui", "path": "web", "package_dir": "web"},
    ]
    print(json.dumps({"surfaces": surfaces, "project": str(root)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
