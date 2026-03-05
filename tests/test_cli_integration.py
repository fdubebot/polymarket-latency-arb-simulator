from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_cli_run_writes_artifacts(tmp_path: Path) -> None:
    outdir = tmp_path / "out"
    cmd = [
        sys.executable,
        "-m",
        "latarb.cli",
        "run",
        "--steps",
        "200",
        "--seed",
        "11",
        "--output-dir",
        str(outdir),
        "--run-name",
        "e2e",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    payload = json.loads(proc.stdout)

    run_dir = outdir / "e2e"
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "fills.csv").exists()
    assert (run_dir / "equity_curve.csv").exists()
    assert payload["result"]["steps"] == 200
