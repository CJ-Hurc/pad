#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
surfaces = [
    {"id": "capability:repository", "kind": "repository", "path": ".", "package_dir": "."},
    {"id": "capability:cli", "kind": "cli", "path": "scripts/complete-e2e/prove.py", "package_dir": "."},
    {"id": "capability:web-ui", "kind": "web-ui", "path": "web", "package_dir": "web"},
]
print(json.dumps({"surfaces": surfaces, "project": str(ROOT)}, indent=2))
