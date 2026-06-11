"""The eval engine's selftest must pass — judges run on this engine's word."""

import subprocess
import sys


def test_selftest_passes():
    p = subprocess.run(
        [sys.executable, "-m", "agentkit.evals", "--selftest"],
        capture_output=True, text=True, timeout=120,
    )
    assert p.returncode == 0, p.stdout + p.stderr
