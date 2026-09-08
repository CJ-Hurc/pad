#!/usr/bin/env python3
"""Canonical complete-e2e entry for Pad (Go PM): go test + CLI + compose YAML."""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def main() -> int:
    print("pad complete-e2e")
    print("----------------------------------------")
    rc = 0
    consumer = HERE / "consumer.py"
    r = subprocess.run([sys.executable, str(consumer)], cwd=str(ROOT))
    if r.returncode == 0:
        print("  PASS  consumer complete-e2e", flush=True)
    else:
        print("  FAIL  consumer complete-e2e", flush=True)
        rc = 1
    print("----------------------------------------")
    print("COMPLETE_E2E: PASS" if rc == 0 else "COMPLETE_E2E: FAIL")
    return rc

if __name__ == "__main__":
    import sys as _sys
    _a = set(_sys.argv[1:])
    if _a & {"-h", "--help"}:
        print("pad-complete-e2e: go test / CLI help / compose validate — no PHPUnit")
        raise SystemExit(0)
    if _a & {"-V", "--version"}:
        print("pad-complete-e2e 1.0.0")
        raise SystemExit(0)
    raise SystemExit(main())
