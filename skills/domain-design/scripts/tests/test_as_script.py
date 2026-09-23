"""``diagram.py`` run as a script, the way a modeller runs it.

Every other test in this package reaches ``diagram`` as an imported module,
with ``conftest.py`` already on ``sys.path``. Nothing exercises the module's
own bootstrap — the ``sys.path.insert`` that finds ``checker/`` by counting
parent directories — so a wrong count there would pass every other test and
only fail for someone typing the command.
"""

import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[4] / "skills" / "domain-design" / "scripts"
    / "diagram.py"
)
CONFORMANCE = Path(__file__).resolve().parents[4] / "contract" / "conformance"
PACKAGE = CONFORMANCE / "01-clean" / "package.yaml"
CYCLIC_PARENT_PACKAGE = (
    CONFORMANCE / "33-a-kind-descending-from-a-cycle" / "package.yaml"
)


def test_run_as_a_script_from_outside_the_scripts_directory(tmp_path):
    # A modeller runs this from the repository root, not from inside
    # ``scripts/``, where ``sys.path.insert`` would find nothing to break.
    # ``tmp_path`` is neither, and further exercises that the bootstrap is
    # not relying on the current working directory at all.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(PACKAGE), "seating"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("classDiagram")
    assert "\n%%" not in result.stdout


def test_run_as_a_script_says_what_it_drew_as_a_mermaid_comment(tmp_path):
    # 01-clean, drawn above, has nothing to say, so it alone would never
    # catch the "%%" convention breaking on the actual command a modeller
    # runs rather than on the imported module. This package does have
    # something to say — "c"'s parent sits on a cycle.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(CYCLIC_PARENT_PACKAGE), "c"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("classDiagram")
    assert "\n%% The parent it names, 'a'" in result.stdout
