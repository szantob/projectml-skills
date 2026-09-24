"""What the command writes, what it prints, and the exit status that says
what kind of answer it is."""

import io
import subprocess
import sys
from pathlib import Path

import dialect
import edit

SCRIPT = Path(__file__).resolve().parents[1] / "edit.py"

BUILDING = "00000000-0000-4000-8000-000000000001"
VENTILATION = "00000000-0000-4000-8000-000000000002"

PACKAGE = """schemaVersion: 4
name: "Building services"
version: ""
valueDomains: []
kinds:
  - id: 00000000-0000-4000-8000-000000000001
    name: "Building"
    text: ""
    whenItApplies: ""
    parameters: []
    rules: []
    howItWouldBeVerified: ""
    wordingRule: ""
    specialises: null
  - id: 00000000-0000-4000-8000-000000000002
    name: "Ventilation"
    text: "Serves the whole Building."
    whenItApplies: ""
    parameters: []
    rules: []
    howItWouldBeVerified: ""
    wordingRule: ""
    specialises: 00000000-0000-4000-8000-000000000001
"""


def _package(tmp_path, text=PACKAGE, name="package.yaml"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _run(*argv, stdin=""):
    out = io.StringIO()
    status = edit.run(list(argv), out, io.StringIO(stdin))
    return status, out.getvalue()


def test_move_writes_the_package_and_names_its_candidates(tmp_path):
    path = _package(tmp_path)
    status, printed = _run("move", str(path), VENTILATION, "--to-root")
    assert status == 0
    kinds = dialect.load(path.read_text(encoding="utf-8"))["kinds"]
    assert kinds[1]["specialises"] is None
    assert kinds[1]["text"] == "Serves the whole Building."
    assert "Candidates" in printed and "'Building'" in printed


def test_a_refusal_leaves_the_file_byte_identical(tmp_path):
    path = _package(tmp_path)
    before = path.read_bytes()
    status, printed = _run("move", str(path), BUILDING, "--under", VENTILATION)
    assert status == 1
    assert "inside the subtree" in printed
    assert path.read_bytes() == before


def test_nothing_to_change_leaves_the_file_byte_identical(tmp_path):
    path = _package(tmp_path)
    before = path.read_bytes()
    status, _ = _run("move", str(path), VENTILATION, "--under", BUILDING)
    assert status == 0
    assert path.read_bytes() == before


def test_set_reads_a_dash_from_stdin_less_one_line_break(tmp_path):
    path = _package(tmp_path)
    status, _ = _run(
        "set", str(path), VENTILATION, "text", "-", stdin="Line one.\nLine two.\n"
    )
    assert status == 0
    kinds = dialect.load(path.read_text(encoding="utf-8"))["kinds"]
    assert kinds[1]["text"] == "Line one.\nLine two."


def test_set_refuses_the_identity(tmp_path):
    path = _package(tmp_path)
    status, printed = _run("set", str(path), VENTILATION, "id", "airflow")
    assert status == 1
    assert "never edited" in printed


def test_create_prints_the_identity_it_generated(tmp_path):
    path = _package(tmp_path)
    status, printed = _run(
        "create", str(path), "--under", VENTILATION, "--name", "Air handler"
    )
    assert status == 0
    created = dialect.load(path.read_text(encoding="utf-8"))["kinds"][-1]
    assert created["id"] in printed
    assert created["name"] == "Air handler"


def test_extract_writes_a_new_file_and_leaves_the_source(tmp_path):
    path = _package(tmp_path)
    before = path.read_bytes()
    output = tmp_path / "extract.yaml"
    status, _ = _run("extract", str(path), VENTILATION, str(output))
    assert status == 0
    assert path.read_bytes() == before
    assert [k["id"] for k in dialect.load(output.read_text("utf-8"))["kinds"]] == [
        BUILDING,
        VENTILATION,
    ]


def test_extract_never_overwrites(tmp_path):
    path = _package(tmp_path)
    output = _package(tmp_path, "keep\n", "extract.yaml")
    status, _ = _run("extract", str(path), VENTILATION, str(output))
    assert status == 1
    assert output.read_text("utf-8") == "keep\n"


def test_json_is_nothing_to_work_from(tmp_path):
    path = _package(tmp_path, '{"schemaVersion": 3}', "package.json")
    status, printed = _run("delete", str(path), VENTILATION)
    assert status == 2
    assert "YAML" in printed


def test_a_package_outside_the_schema_is_nothing_to_work_from(tmp_path):
    path = _package(tmp_path, "schemaVersion: 3\n")
    status, printed = _run("delete", str(path), VENTILATION)
    assert status == 2
    assert "schema" in printed


def test_an_unreadable_file_is_nothing_to_work_from(tmp_path):
    path = _package(tmp_path, "a: 1\na: 2\n")
    status, _ = _run("delete", str(path), VENTILATION)
    assert status == 2


def test_a_malformed_command_is_nothing_to_work_from(tmp_path, capsys):
    status, _ = _run("move", str(_package(tmp_path)), VENTILATION)
    assert status == 2


def test_it_runs_as_a_script(tmp_path):
    # From another directory, as the skill runs it: the package's, not the
    # skill's.
    path = _package(tmp_path)
    finished = subprocess.run(
        [sys.executable, str(SCRIPT), "delete", str(path), VENTILATION],
        cwd=tmp_path,
        capture_output=True,
        encoding="utf-8",
    )
    assert finished.returncode == 0, finished.stdout + finished.stderr
    kinds = dialect.load(path.read_text(encoding="utf-8"))["kinds"]
    assert [k["id"] for k in kinds] == [BUILDING]
