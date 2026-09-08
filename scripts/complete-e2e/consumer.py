#!/usr/bin/env python3
"""Live Pad proofs: go test (scoped), CLI --help, docker-compose.yml structure."""
from __future__ import annotations
import os, re, subprocess, sys, time
from pathlib import Path
from shutil import which
ROOT = Path(__file__).resolve().parents[2]

def step(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    extra = f" — {detail}" if detail else ""
    print(f"  {status}  {name}{extra}", flush=True)

def ensure_embed_placeholder() -> None:
    build = ROOT / "web" / "build"
    build.mkdir(parents=True, exist_ok=True)
    if not any(build.iterdir()):
        (build / ".gitkeep").write_text("placeholder\n")

def validate_compose(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, f"missing {path.name}"
    text = path.read_text(errors="replace")
    if "services:" not in text:
        return False, "no services: key"
    return True, f"{path.name} structural ok ({len(text)} bytes)"

def write_junit(fails: int) -> None:
    junit_dir = Path(os.environ.get("HURC_COMPLETE_E2E_JUNIT") or (ROOT / ".hurc-harness/state/complete-e2e/junit"))
    junit_dir.mkdir(parents=True, exist_ok=True)
    if fails:
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<testsuite name="pad-consumer" tests="1" failures="{fails}" errors="0">\n'
            '  <testcase classname="pad" name="consumer">\n'
            '    <failure message="consumer failed"/>\n'
            '  </testcase>\n'
            '</testsuite>\n'
        )
    else:
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuite name="pad-consumer" tests="1" failures="0" errors="0">\n'
            '  <testcase classname="pad" name="consumer"/>\n'
            '</testsuite>\n'
        )
    (junit_dir / "pad-consumer.xml").write_text(body)

def main() -> int:
    print("pad consumer proofs", flush=True)
    fails = 0
    env = os.environ.copy()
    env.setdefault("CGO_ENABLED", "0")

    pkgs = []
    for p in ["./internal/cmdhelp/...", "./internal/models/..."]:
        probe = ROOT / p.replace("./", "").replace("/...", "")
        if probe.exists():
            pkgs.append(p)
    if not pkgs:
        pkgs = ["./internal/cli/..."]

    t0 = time.time()
    r = subprocess.run(
        ["go", "test", *pkgs, "-count=1", "-timeout", "120s"],
        cwd=str(ROOT), env=env, capture_output=True, text=True,
    )
    ok = r.returncode == 0
    detail = f"pkgs={pkgs} elapsed={time.time()-t0:.1f}s"
    if not ok:
        detail += " " + ((r.stderr or r.stdout or "")[-240:].replace("\n", " "))
    step("go test (scoped)", ok, detail)
    if not ok:
        fails += 1

    ensure_embed_placeholder()
    bin_path = ROOT / "pad-ce2e-bin"
    r = subprocess.run(
        ["go", "build", "-o", str(bin_path), "./cmd/pad"],
        cwd=str(ROOT), env=env, capture_output=True, text=True,
    )
    ok = r.returncode == 0 and bin_path.is_file()
    step("go build ./cmd/pad", ok, (r.stderr or "")[-200:] if not ok else bin_path.name)
    if not ok:
        fails += 1
    else:
        for args, label in [(["--help"], "cli --help"), (["server", "--help"], "cli server --help")]:
            rr = subprocess.run([str(bin_path), *args], cwd=str(ROOT), capture_output=True, text=True)
            out = (rr.stdout or "") + (rr.stderr or "")
            ok2 = rr.returncode == 0 and ("Usage" in out or "pad" in out.lower() or "server" in out.lower())
            step(label, ok2, f"rc={rr.returncode} bytes={len(out)}")
            if not ok2:
                fails += 1
        try:
            bin_path.unlink(missing_ok=True)
        except TypeError:
            try:
                bin_path.unlink()
            except OSError:
                pass

    compose = ROOT / "docker-compose.yml"
    if which("docker"):
        rr = subprocess.run(
            ["docker", "compose", "-f", str(compose), "config", "-q"],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        ok = rr.returncode == 0
        step("docker compose config -q", ok, (rr.stderr or "")[-160:] if not ok else "ok")
        if not ok:
            fails += 1
    else:
        ok, detail = validate_compose(compose)
        step("docker-compose.yml structural validate (no docker binary)", ok, detail)
        if not ok:
            fails += 1
        for extra in ["docker-compose.prod.yml", "docker-compose.test.yml"]:
            p = ROOT / extra
            if p.is_file():
                ok2, detail2 = validate_compose(p)
                step(f"{extra} structural", ok2, detail2)
                if not ok2:
                    fails += 1

    write_junit(fails)
    return 1 if fails else 0

if __name__ == "__main__":
    raise SystemExit(main())
