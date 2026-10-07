"""The bundle, unpacked where claude.ai would put it, and used.

What a bundle holds is checked on its list of names; whether it works is
checked by running the scripts from an unpacked copy that has no repository
around it, so a script that still reached for the repository's checker would
fail here rather than for someone who uploaded it.
"""

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "release"))

import bundle  # noqa: E402

CONFORMANCE = ROOT / "contract" / "conformance"
CLEAN = CONFORMANCE / "01-clean" / "package.yaml"
DUPLICATE_PARAMETER = CONFORMANCE / "04-duplicate-parameter-name" / "package.yaml"
SECOND = "00000000-0000-4000-8000-000000000002"


def _unpacked(tmp_path):
    # A skills folder of its own, far from the repository: nothing four
    # levels above a script there is a checker.
    target = bundle.build(tmp_path / "out")
    skills = tmp_path / "mounted" / "skills" / "user"
    skills.mkdir(parents=True)
    with zipfile.ZipFile(target) as archive:
        archive.extractall(skills)
    return skills / bundle.SKILL


def _run(script, *arguments, cwd):
    return subprocess.run(
        [sys.executable, str(script), *map(str, arguments)],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_holds_one_folder_with_the_skill_and_what_it_runs_on(tmp_path):
    with zipfile.ZipFile(bundle.build(tmp_path)) as archive:
        names = archive.namelist()
    assert {name.split("/")[0] for name in names} == {bundle.SKILL}
    for needed in (
        "SKILL.md",
        "scripts/diagram.py",
        "scripts/edit.py",
        "checker/check.py",
        "checker/requirements.txt",
        "contract/package.schema.json",
    ):
        assert f"{bundle.SKILL}/{needed}" in names


def test_leaves_out_what_only_works_on_the_repository(tmp_path):
    with zipfile.ZipFile(bundle.build(tmp_path)) as archive:
        names = archive.namelist()
    for name in names:
        parts = name.split("/")
        assert "tests" not in parts
        assert "__pycache__" not in parts
        assert "conformance" not in parts
        assert not name.endswith((".pyc", "requirements-dev.txt"))


def test_the_same_commit_builds_the_same_bytes(tmp_path):
    first = bundle.build(tmp_path / "first").read_bytes()
    second = bundle.build(tmp_path / "second").read_bytes()
    assert first == second


def test_the_unpacked_checker_checks(tmp_path):
    skill = _unpacked(tmp_path)
    clean = _run(skill / "checker" / "check.py", CLEAN, cwd=tmp_path)
    assert clean.returncode == 0, clean.stdout + clean.stderr
    issue = _run(skill / "checker" / "check.py", DUPLICATE_PARAMETER, cwd=tmp_path)
    assert issue.returncode == 1, issue.stdout + issue.stderr
    assert "duplicate-parameter-name" in issue.stdout


def test_the_unpacked_diagram_finds_the_checker_inside_the_skill(tmp_path):
    skill = _unpacked(tmp_path)
    result = _run(skill / "scripts" / "diagram.py", CLEAN, SECOND, cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("classDiagram")


def test_the_unpacked_edit_writes_a_package_the_checker_accepts(tmp_path):
    skill = _unpacked(tmp_path)
    package = tmp_path / "package.yaml"
    package.write_bytes(CLEAN.read_bytes())
    edited = _run(
        skill / "scripts" / "edit.py",
        "set", package, SECOND, "name", "Seats",
        cwd=tmp_path,
    )
    assert edited.returncode == 0, edited.stdout + edited.stderr
    checked = _run(skill / "checker" / "check.py", package, cwd=tmp_path)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert "Seats" in package.read_text(encoding="utf-8")
