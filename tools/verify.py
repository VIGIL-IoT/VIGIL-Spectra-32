"""Run the repository's pinned local verification suite in one command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, arguments: list[str]) -> bool:
    print(f"\n== {name} ==", flush=True)
    result = subprocess.run(arguments, cwd=ROOT, check=False)
    return result.returncode == 0


def main() -> int:
    python = sys.executable
    steps = (
        (
            "Ruff correctness checks",
            [python, "-m", "ruff", "check", "--select", "E4,E7,E9,F", "data", "services", "components", "simulator", "tests", "tools"],
        ),
        (
            "Compile project Python modules",
            [python, "-m", "compileall", "-q", "data", "services", "components", "simulator", "tests", "tools"],
        ),
        ("Documentation links and text hygiene", [python, "tools/check_docs.py"]),
        ("Unit and dashboard tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("Locked dependency audit", [python, "-m", "pip_audit"]),
    )
    failed: list[str] = []
    for name, arguments in steps:
        if not run_step(name, arguments):
            failed.append(name)
    if failed:
        print("\nVerification failed:", ", ".join(failed))
        return 1
    print("\nAll local verification steps passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
