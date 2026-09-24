"""A missing dependency is nothing to work from, said in words.

A fresh machine may well lack PyYAML or jsonschema. The checker says so and
exits 2; the skill's scripts must too, rather than end in a traceback whose
exit status, 1, would read as "refused" - a verdict about the package, when
nothing was ever read.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]


def _run_without(module, script, tmp_path):
    blocked = tmp_path / "blocked"
    (blocked / module).mkdir(parents=True)
    (blocked / module / "__init__.py").write_text(
        f"raise ImportError('blocked for a test', name={module!r})\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PYTHONPATH": str(blocked)}
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), "package.yaml", "anything"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        encoding="utf-8",
    )


@pytest.mark.parametrize("script", ["edit.py", "diagram.py"])
@pytest.mark.parametrize("module", ["yaml", "jsonschema"])
def test_a_missing_dependency_exits_two_and_names_it(script, module, tmp_path):
    finished = _run_without(module, script, tmp_path)
    assert finished.returncode == 2, finished.stdout + finished.stderr
    assert "Traceback" not in finished.stderr
    assert module in finished.stdout
    assert "pip install -r" in finished.stdout
